import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateField, addItem, removeItem, resetForm } from '../store/slices/formSlice';
import { createInteraction, updateInteraction } from '../api/interactionsApi';

const MainForm = () => {
  const formData = useSelector((state) => state.form);
  const dispatch = useDispatch();
  const [newItem, setNewItem] = useState({ attendees: '', materials: '', samples: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    dispatch(updateField({ field: name, value }));
  };

  const handleAddArrayItem = (field, key) => {
    if (!newItem[key].trim()) return;
    dispatch(addItem({ field, item: newItem[key] }));
    setNewItem({ ...newItem, [key]: '' });
  };

  const handleSubmit = async (status) => {
    setIsSubmitting(true);
    try {
      const payload = { ...formData, status };
      const { interaction_id, ...dataToSave } = payload;
      
      let result;
      if (interaction_id) {
        // If we have an ID, it's an update
        result = await updateInteraction(interaction_id, dataToSave);
        alert(`Success! Interaction ${status === 'Draft' ? 'updated' : 'submitted'}.`);
      } else {
        // Otherwise, it's a new record
        result = await createInteraction(dataToSave);
        alert(`Success! Interaction ${status === 'Draft' ? 'saved' : 'submitted'}.`);
      }

      if (status === 'Submitted') {
        dispatch(resetForm());
      } else {
        dispatch(updateField({ field: 'interaction_id', value: result.id }));
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  const labelStyle = "text-[9px] font-black text-blue-400 uppercase tracking-[0.2em] mb-2 block ml-1";
  const inputStyle = "w-full px-4 py-3 bg-black/40 border border-white/10 rounded-xl text-sm text-white placeholder:text-slate-500 focus:outline-none focus:border-blue-400/50 focus:ring-2 focus:ring-blue-500/10 transition-all duration-300";

  return (
    <div className="max-w-4xl mx-auto p-8 bg-slate-900/40 backdrop-blur-3xl border border-white/5 rounded-[40px] shadow-2xl my-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex justify-between items-start mb-8">
        <div>
          <h1 className="text-3xl font-black tracking-tighter text-white">
            Log HCP Interaction
          </h1>
          <p className="text-blue-400/80 mt-1 font-bold text-sm tracking-tight italic">Intelligence for the Field</p>
        </div>
        <div className={`px-4 py-1.5 rounded-full text-[8px] font-black uppercase tracking-[0.2em] border shadow-md ${formData.status === 'Draft' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'}`}>
          {formData.status}
        </div>
      </div>

      <div className="space-y-8">
        {/* Row 1: Name & Interaction Type */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label className={labelStyle}>HCP Name</label>
            <input type="text" name="hcp_name" value={formData.hcp_name} onChange={handleChange} placeholder="e.g. Dr. Kalki" className={inputStyle} />
          </div>
          <div>
            <label className={labelStyle}>Interaction Type</label>
            <select name="interaction_type" value={formData.interaction_type} onChange={handleChange} className={inputStyle}>
              <option value="Meeting">Meeting</option>
              <option value="Virtual">Virtual Call</option>
              <option value="Email">Email</option>
              <option value="Phone">Phone Call</option>
            </select>
          </div>
        </div>

        {/* Row 2: Date & Time */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div>
            <label className={labelStyle}>Date</label>
            <input type="date" name="interaction_date" value={formData.interaction_date} onChange={handleChange} className={inputStyle} />
          </div>
          <div>
            <label className={labelStyle}>Time</label>
            <input type="time" name="interaction_time" value={formData.interaction_time} onChange={handleChange} className={inputStyle} />
          </div>
        </div>

        {/* Row 3: Attendees */}
        <div className="space-y-4">
          <label className={labelStyle}>Attendees</label>
          <div className="flex space-x-2">
            <input type="text" value={newItem.attendees} onChange={(e) => setNewItem({...newItem, attendees: e.target.value})} placeholder="Add participant..." className={inputStyle} />
            <button onClick={() => handleAddArrayItem('attendees', 'attendees')} className="px-6 bg-white/10 hover:bg-white/20 text-white rounded-xl font-bold uppercase tracking-widest text-[9px] border border-white/10 transition-all active:scale-95">Add</button>
          </div>
          <div className="flex flex-wrap gap-2">
            {formData.attendees.map((name, i) => (
              <span key={i} className="flex items-center space-x-2 px-3 py-1.5 bg-blue-500/10 text-blue-300 border border-blue-500/20 rounded-lg text-xs font-bold animate-in zoom-in duration-300">
                <span>{name}</span>
                <button onClick={() => dispatch(removeItem({field: 'attendees', index: i}))} className="text-blue-500/50 hover:text-red-400 transition-colors">&times;</button>
              </span>
            ))}
          </div>
        </div>

        {/* Row 4: Topics Discussed */}
        <div className="space-y-3">
          <label className={labelStyle}>Topics Discussed</label>
          <textarea 
            name="topics_discussed" 
            value={formData.topics_discussed} 
            onChange={handleChange} 
            rows={4} 
            placeholder="Key discussion points..."
            className={`${inputStyle} resize-none leading-relaxed text-xs`} 
          />
        </div>

        {/* Row 5: Materials & Samples */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-4">
            <label className={labelStyle}>Materials Shared</label>
            <div className="flex space-x-2">
              <input type="text" value={newItem.materials} onChange={(e) => setNewItem({...newItem, materials: e.target.value})} placeholder="Add material..." className={`${inputStyle} text-xs`} />
              <button onClick={() => handleAddArrayItem('materials_shared', 'materials')} className="px-3 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">+</button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.materials_shared.map((item, i) => (
                <span key={i} className="px-3 py-1 bg-white/5 border border-white/5 rounded-lg text-[9px] text-slate-500 font-bold flex items-center space-x-2">
                  <span>{item}</span>
                  <button onClick={() => dispatch(removeItem({field: 'materials_shared', index: i}))} className="hover:text-red-400">&times;</button>
                </span>
              ))}
            </div>
          </div>
          <div className="space-y-4">
            <label className={labelStyle}>Samples Distributed</label>
            <div className="flex space-x-2">
              <input type="text" value={newItem.samples} onChange={(e) => setNewItem({...newItem, samples: e.target.value})} placeholder="Add sample..." className={`${inputStyle} text-xs`} />
              <button onClick={() => handleAddArrayItem('samples_distributed', 'samples')} className="px-3 bg-white/5 rounded-xl border border-white/10 hover:bg-white/10 transition-all">+</button>
            </div>
            <div className="flex flex-wrap gap-2">
              {formData.samples_distributed.map((item, i) => (
                <span key={i} className="px-3 py-1 bg-white/5 border border-white/5 rounded-lg text-[9px] text-slate-500 font-bold flex items-center space-x-2">
                  <span>{item}</span>
                  <button onClick={() => dispatch(removeItem({field: 'samples_distributed', index: i}))} className="hover:text-red-400">&times;</button>
                </span>
              ))}
            </div>
          </div>
        </div>

        {/* Row 6: Sentiment */}
        <div className="p-8 bg-black/40 rounded-[32px] border border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
          <label className={labelStyle + " mb-0"}>Sentiment</label>
          <div className="flex space-x-3">
            {['Positive', 'Neutral', 'Negative'].map((s) => (
              <label key={s} className="cursor-pointer">
                <input type="radio" name="sentiment" value={s} checked={formData.sentiment === s} onChange={handleChange} className="hidden" />
                <span className={`px-6 py-2 rounded-xl text-xs font-black transition-all duration-500 inline-block border ${formData.sentiment === s ? 'bg-blue-600 text-white border-blue-400 shadow-lg scale-105' : 'bg-white/5 text-slate-500 border-white/5 hover:border-white/20 hover:text-slate-300'}`}>
                  {s}
                </span>
              </label>
            ))}
          </div>
        </div>

        {/* Row 10: Outcomes & Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-3">
            <label className={labelStyle}>Outcomes</label>
            <textarea name="outcomes" value={formData.outcomes} onChange={handleChange} rows={4} placeholder="Summary of results..." className={`${inputStyle} resize-none leading-relaxed text-xs`} />
          </div>
          <div className="space-y-3">
            <label className={labelStyle}>Follow-up Actions</label>
            <textarea name="follow_up_actions" value={formData.follow_up_actions} onChange={handleChange} rows={4} placeholder="Next steps..." className={`${inputStyle} resize-none leading-relaxed text-xs`} />
          </div>
        </div>

        {/* Actions */}
        <div className="pt-8 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-6">
          <button 
            disabled={isSubmitting} 
            onClick={() => handleSubmit('Draft')} 
            className="flex-1 py-4 bg-white/5 hover:bg-white/10 text-white font-black uppercase tracking-[0.2em] text-[10px] rounded-2xl border border-white/10 transition-all active:scale-95 disabled:opacity-50"
          >
            {isSubmitting ? 'Saving...' : 'Save Draft'}
          </button>
          <button 
            disabled={isSubmitting} 
            onClick={() => handleSubmit('Submitted')} 
            className="flex-[2] py-4 bg-blue-600 hover:bg-blue-500 text-white font-black uppercase tracking-[0.2em] text-[10px] rounded-2xl shadow-xl transition-all active:scale-95 disabled:opacity-50"
          >
            {isSubmitting ? 'Submitting...' : 'Log Interaction'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default MainForm;
