import type { TraceData } from '../types';

interface RunsProps {
  traces: TraceData[];
  onSelectRun: (runId: string) => void;
}

export function Runs({ traces, onSelectRun }: RunsProps) {
  return (
    <div className="instrument-panel overflow-hidden">
      <div className="p-4 border-b border-line flex justify-between items-center bg-line/20">
        <h3 className="font-heading text-lg font-medium text-ink">
          AGENT_RUNS
        </h3>
        <span className="font-mono text-xs text-inkMuted">[{traces.length} RECORDED]</span>
      </div>
      
      {traces.length === 0 ? (
        <div className="p-8 text-center font-mono text-xs text-inkMuted uppercase">No data blocks found.</div>
      ) : (
        <div className="divide-y divide-line">
          {traces.map(trace => (
            <button
              key={trace.run_id}
              onClick={() => onSelectRun(trace.run_id)}
              className="w-full text-left p-4 hover:bg-line/30 transition-colors duration-0 flex items-center justify-between group"
            >
              <div>
                <div className="font-sans font-medium text-ink mb-1 group-hover:text-signal transition-colors">{trace.task}</div>
                <div className="font-mono text-xs text-inkMuted flex gap-4">
                  <span>AGNT:{trace.agent_name}</span>
                  <span>ID:{trace.run_id.substring(0,8)}</span>
                  <span>TS:{new Date(trace.started_at).toISOString().split('T')[1].split('.')[0]}</span>
                </div>
              </div>
              <div>
                <span className={`px-2 py-0.5 font-mono text-[10px] font-bold uppercase border ${trace.final_status === 'success' ? 'border-signal text-signal' : 'border-fail text-fail'}`}>
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
