import { useState, useCallback } from 'react';
import { Sidebar } from './components/Sidebar';
import { Overview } from './views/Overview';
import { Runs } from './views/Runs';
import { PlanAndTrace } from './views/PlanAndTrace';
import { Memory } from './views/Memory';
import { Architecture } from './views/Architecture';
import type { TraceData } from './types';

function App() {
  const [currentView, setCurrentView] = useState('overview');
  const [traces, setTraces] = useState<TraceData[]>([]);
  const [selectedRunId, setSelectedRunId] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFiles = useCallback((files: FileList | File[]) => {
    Array.from(files).forEach(file => {
      if (file.type === "application/json" || file.name.endsWith(".json")) {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const data = JSON.parse(e.target?.result as string);
            // Basic validation
            if (data.run_id && data.plan && data.steps) {
              setTraces(prev => {
                // Prevent duplicates
                if (prev.some(t => t.run_id === data.run_id)) return prev;
                return [...prev, data as TraceData];
              });
            }
          } catch (err) {
            console.error("Failed to parse JSON", err);
          }
        };
        reader.readAsText(file);
      }
    });
  }, []);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleSelectRun = (runId: string) => {
    setSelectedRunId(runId);
    setCurrentView('plan');
  };

  return (
    <div 
      className={`min-h-screen relative flex ${isDragging ? 'bg-accentCyan/5' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      <main className="flex-1 ml-64 p-8 relative">
        {/* Glow Effects */}
        <div className="fixed top-0 left-1/4 w-96 h-96 bg-accentCyan/20 rounded-full blur-[120px] -z-10 pointer-events-none" />
        <div className="fixed bottom-0 right-1/4 w-96 h-96 bg-accentPurple/20 rounded-full blur-[120px] -z-10 pointer-events-none" />

        <div className="max-w-6xl mx-auto space-y-6">
          <header className="flex justify-between items-center bg-bgPanel/50 backdrop-blur-md border border-white/5 p-4 rounded-xl">
            <div className="text-textMuted flex items-center gap-2">
              <span className="font-medium text-white">Dashboard</span>
              <span>/</span>
              <span className="capitalize">{currentView.replace('-', ' ')}</span>
            </div>
            <div>
              <label className="cursor-pointer bg-accentCyan/10 text-accentCyan hover:bg-accentCyan hover:text-bgBase transition-all duration-300 font-medium px-4 py-2 rounded-lg flex items-center gap-2 text-sm shadow-[0_0_10px_rgba(34,211,238,0.2)]">
                <span>+ Load Trace</span>
                <input 
                  type="file" 
                  accept=".json" 
                  multiple 
                  className="hidden" 
                  onChange={(e) => e.target.files && handleFiles(e.target.files)}
                />
              </label>
            </div>
          </header>

          <div className="min-h-[80vh]">
            {currentView === 'overview' && <Overview traces={traces} />}
            {currentView === 'runs' && <Runs traces={traces} onSelectRun={handleSelectRun} />}
            {currentView === 'plan' && <PlanAndTrace traces={traces} selectedRunId={selectedRunId} />}
            {currentView === 'memory' && <Memory />}
            {currentView === 'arch' && <Architecture />}
          </div>
        </div>
      </main>

      {isDragging && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm pointer-events-none border-4 border-dashed border-accentCyan/50 m-4 rounded-2xl">
          <div className="text-center p-12 glass-panel rounded-2xl">
            <div className="text-6xl text-accentCyan mb-4 animate-bounce">◈</div>
            <h2 className="text-2xl font-bold text-white mb-2">Drop Trace Files</h2>
            <p className="text-accentCyan/80">Release to load JSON trace files</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
