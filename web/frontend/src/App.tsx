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
  const [error, setError] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "";

  useEffect(() => {
    // Attempt to fetch from API on mount
    fetch(`${API_BASE}/api/runs`)
      .then(res => {
        if (!res.ok) throw new Error("API not available");
        return res.json();
      })
      .then(async (summaries: any[]) => {
        // Fetch full traces for each summary
        const fullTraces = await Promise.all(
          summaries.map(s => 
            fetch(`${API_BASE}/api/runs/${s.run_id}`).then(r => r.json())
          )
        );
        setTraces(fullTraces);
      })
      .catch(err => {
        console.log("Not running in live-server mode or API unavailable:", err);
      });
  }, [API_BASE]);

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
      className={`min-h-screen relative flex ${isDragging ? 'bg-signal/5' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />
      
      <main className="flex-1 ml-64 p-8 relative">
        <div className="max-w-6xl mx-auto space-y-6">
          <header className="flex justify-between items-center instrument-panel px-4 py-3">
            <div className="text-inkMuted flex items-center gap-2 font-mono text-sm">
              <span className="text-ink">INSTRUMENT</span>
              <span>/</span>
              <span className="uppercase text-signal">{currentView.replace('-', ' ')}</span>
            </div>
            <div>
              <label className="cursor-pointer border border-signal text-signal hover:bg-signal hover:text-bgBase transition-colors duration-0 font-mono text-xs px-3 py-1.5 rounded-sm flex items-center gap-2">
                <span>LOAD_TRACE</span>
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-bgBase/80 pointer-events-none border border-signal m-4">
          <div className="text-center font-mono">
            <div className="text-2xl text-signal mb-2 animate-pulse">AWAITING_INPUT</div>
            <p className="text-inkMuted text-sm">RELEASE TO PARSE SEQUENCE</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
