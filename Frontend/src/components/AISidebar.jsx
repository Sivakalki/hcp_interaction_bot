import React, { useState, useRef, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { sendMessage, clearChat } from '../store/slices/aiSlice';
import { populateFromAI } from '../store/slices/formSlice';

// Simple component to render Markdown-style tables from AI text
const MarkdownTable = ({ content }) => {
  const lines = content.trim().split('\n');
  const tableLines = lines.filter(l => l.includes('|'));

  if (tableLines.length < 3) return <p className="whitespace-pre-wrap">{content}</p>;

  const headers = tableLines[0].split('|').filter(h => h.trim()).map(h => h.trim());
  const rows = tableLines.slice(2).map(row =>
    row.split('|').filter(r => r.trim() !== undefined).map(r => r.trim()).filter(r => r !== '')
  );

  return (
    <div className="my-4 overflow-x-auto rounded-xl border border-white/10 bg-black/20">
      <table className="w-full text-left border-collapse text-[10px]">
        <thead>
          <tr className="bg-white/5">
            {headers.map((h, i) => (
              <th key={i} className="px-4 py-3 font-black text-blue-400 uppercase tracking-widest border-b border-white/5">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
              {row.map((cell, j) => (
                <td key={j} className="px-4 py-3 text-slate-300 font-medium font-mono truncate max-w-[150px]" title={cell}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

const AISidebar = () => {
  const [input, setInput] = useState('');
  const { messages, status, sessionId } = useSelector((state) => state.ai);
  const dispatch = useDispatch();
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || status === 'loading') return;

    const userMessage = input;
    setInput('');

    try {
      const resultAction = await dispatch(sendMessage({ content: userMessage, sessionId }));
      if (sendMessage.fulfilled.match(resultAction)) {
        const response = resultAction.payload;
        if (response.form_updates && response.form_updates.length > 0) {
          dispatch(populateFromAI(response.form_updates));
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const renderMessageContent = (content) => {
    if (content.includes('|') && content.includes('\n|')) {
      // Split content into text and table parts if necessary
      return <MarkdownTable content={content} />;
    }
    return <p className="whitespace-pre-wrap">{content}</p>;
  };

  return (
    <div className="flex flex-col h-full bg-[#020617] text-slate-100 border-l border-white/5 font-sans">
      {/* Header */}
      <div className="p-6 border-b border-white/5 bg-black/40 backdrop-blur-2xl sticky top-0 z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600/30 rounded-xl flex items-center justify-center text-xl border border-blue-500/40">
              🤖
            </div>
            <div>
              <h2 className="text-lg font-black text-white tracking-tighter">AI Assistant</h2>
              <div className="flex items-center space-x-2 mt-0.5">
                <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></span>
                <span className="text-[8px] uppercase tracking-[0.2em] text-blue-400 font-black">Log interaction via chat</span>
              </div>
            </div>
          </div>
          <button
            onClick={() => dispatch(clearChat())}
            className="p-2.5 text-slate-600 hover:text-red-500 transition-all hover:bg-red-500/10 rounded-xl"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto scrollbar-hide p-6 space-y-6 bg-gradient-to-b from-transparent to-black/40">
        {messages.length === 0 && (
          <div className="bg-blue-600/5 border border-blue-600/10 rounded-[24px] p-6 text-center animate-in zoom-in duration-700">
            <div className="w-12 h-12 bg-blue-600/20 rounded-[16px] mx-auto mb-4 flex items-center justify-center text-2xl">⚡</div>
            <p className="text-xs text-slate-500 leading-relaxed font-bold italic">
              "Met Dr. Kalki today. Discussion was focused on cardiovascular research. Sentiment was very positive."
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-500`}>
            <div className={`max-w-[95%] px-5 py-3 rounded-[20px] text-xs leading-relaxed shadow-lg ${msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-none font-bold'
                : msg.isError
                  ? 'bg-red-500/20 border-2 border-red-500/40 text-red-200 rounded-bl-none shadow-red-500/10 font-bold'
                  : 'bg-slate-900 border border-white/10 text-slate-300 rounded-bl-none'
              }`}>
              {renderMessageContent(msg.content)}
            </div>
          </div>
        ))}

        {status === 'loading' && (
          <div className="flex justify-start">
            <div className="flex space-x-2 p-3 bg-black/40 rounded-full border border-white/10">
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.1s]"></div>
              <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce [animation-delay:0.2s]"></div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-6 bg-black/60 border-t border-white/5 backdrop-blur-3xl">
        <div className="relative group scrollbar-hide">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); } }}
            placeholder="Type details..."
            className="w-full bg-slate-950/80 border border-white/5 group-focus-within:border-blue-500/50 rounded-[20px] px-5 py-4 text-xs text-white placeholder:text-slate-600 focus:outline-none transition-all duration-500 pr-16 min-h-[60px] max-h-[200px]"
            rows={1}
            style={{ resize: 'none' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || status === 'loading'}
            className="absolute right-3 bottom-3 w-10 h-10 bg-blue-600 hover:bg-blue-500 text-white rounded-[14px] flex items-center justify-center shadow-lg transition-all active:scale-90 disabled:opacity-0 cursor-pointer"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 transform rotate-90" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AISidebar;
