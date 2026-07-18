import type { TraceData } from '../types';

interface RunsProps {
  traces: TraceData[];
  onSelectRun: (runId: string) => void;
}

export function Runs({ traces, onSelectRun }: RunsProps) {
  return (
    <div className="glass-card overflow-hidden">
      <div className="p-4 border-b border-white/5 flex justify-between items-center bg-black/20">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <span className="text-accentCyan">▤</span> Agent Runs
        </h3>
        <span className="text-sm text-accentCyan font-medium">{traces.length} runs</span>
      </div>
      
      {traces.length === 0 ? (
        <div className="p-8 text-center text-textMuted">No runs loaded yet.</div>
      ) : (
        <div className="divide-y divide-white/5">
          {traces.map(trace => (
            <button
              key={trace.run_id}
              onClick={() => onSelectRun(trace.run_id)}
              className="w-full text-left p-4 hover:bg-white/5 transition-colors duration-200 flex items-center justify-between group"
            >
              <div>
                <div className="font-medium text-white mb-1 group-hover:text-accentCyan transition-colors">{trace.task}</div>
                <div className="text-xs text-textMuted flex gap-3">
                  <span><span className="opacity-50">Agent:</span> {trace.agent_name}</span>
                  <span><span className="opacity-50">ID:</span> <span className="font-mono">{trace.run_id.substring(0,8)}...</span></span>
                  <span><span className="opacity-50">Started:</span> {new Date(trace.started_at).toLocaleString()}</span>
                </div>
              </div>
              <div>
                <span className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${trace.final_status === 'success' ? 'bg-accentGreen/20 text-accentGreen' : 'bg-red-500/20 text-red-500'}`}>
                  {trace.final_status}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
