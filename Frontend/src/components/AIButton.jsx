import React from 'react';
import { useDispatch } from 'react-redux';
import { toggleSidebar } from '../store/slices/aiSlice';

const AIButton = () => {
  const dispatch = useDispatch();

  return (
    <button
      onClick={() => dispatch(toggleSidebar())}
      className="fixed bottom-8 right-8 w-16 h-16 bg-primary-500 hover:bg-primary-400 text-white rounded-full shadow-2xl shadow-primary-500/40 flex items-center justify-center transition-all hover:scale-110 active:scale-95 group z-50"
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        className="h-8 w-8 group-hover:rotate-12 transition-transform"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
        />
      </svg>
      <span className="absolute -top-12 right-0 bg-white text-slate-900 text-xs font-bold px-3 py-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-xl">
        Need help?
      </span>
    </button>
  );
};

export default AIButton;
