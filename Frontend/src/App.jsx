import React from 'react';
import MainForm from './components/MainForm';
import AISidebar from './components/AISidebar';

function App() {
  return (
    <div className="flex h-screen w-screen overflow-hidden bg-[#020617] font-inter">
      {/* Left Section: Main Interaction Form (70%) */}
      <div className="w-[70%] h-full overflow-y-auto scrollbar-hide px-4 py-2">
        <MainForm />
      </div>

      {/* Right Section: AI Assistant Sidebar (30%) */}
      <div className="w-[30%] h-full overflow-hidden flex flex-col border-l border-white/5 shadow-2xl">
        <AISidebar />
      </div>
    </div>
  );
}

export default App;
