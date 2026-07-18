import type { TraceData } from '../types';

interface OverviewProps {
  traces: TraceData[];
}

export function Overview({ traces }: OverviewProps) {
  const successfulRuns = traces.filter(t => t.final_status === 'success').length;
  const totalHeals = traces.reduce((acc, t) => acc + t.steps.reduce((sAcc, s) => sAcc + (s.retries || 0), 0), 0);
  const totalToolCalls = traces.reduce((acc, t) => acc + t.steps.reduce((sAcc, s) => sAcc + s.tool_calls.length, 0), 0);
  // Mocking memory entries count for now as they are not in trace schema
  const memoryEntries = traces.length * 5; 

  const latestRun = traces.length > 0 ? traces[traces.length - 1] : null;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="stat-card">
          <div className="text-4xl font-light text-accentGreen">{successfulRuns}</div>
          <div className="text-sm text-textMuted uppercase tracking-wider font-medium">Successful Runs</div>
        </div>
        <div className="stat-card">
          <div className="text-4xl font-light text-accentAmber">{totalHeals}</div>
          <div className="text-sm text-textMuted uppercase tracking-wider font-medium">Self-Heals</div>
        </div>
        <div className="stat-card">
          <div className="text-4xl font-light text-accentPurple">{totalToolCalls}</div>
          <div className="text-sm text-textMuted uppercase tracking-wider font-medium">Tool Calls</div>
        </div>
        <div className="stat-card">
          <div className="text-4xl font-light text-accentCyan">{memoryEntries}</div>
          <div className="text-sm text-textMuted uppercase tracking-wider font-medium">Memory Entries</div>
        </div>
      </div>

      {latestRun && (
        <div className="glass-card p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-white flex items-center gap-2">
              <span className="text-accentCyan">→</span> Latest Run
            </h3>
            <span className={`px-2.5 py-1 rounded text-xs font-bold uppercase ${latestRun.final_status === 'success' ? 'bg-accentGreen/20 text-accentGreen' : 'bg-red-500/20 text-red-500'}`}>
              {latestRun.final_status}
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between border-b border-white/5 pb-2">
              <span className="text-textMuted">Task</span>
              <span className="text-white font-medium">{latestRun.task}</span>
            </div>
            <div className="flex justify-between border-b border-white/5 py-2">
              <span className="text-textMuted">Agent</span>
              <span className="text-white">{latestRun.agent_name}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-textMuted">Run ID</span>
              <span className="text-xs text-textMuted font-mono bg-black/30 px-2 py-1 rounded">{latestRun.run_id}</span>
            </div>
          </div>
        </div>
      )}

      {traces.length === 0 && (
        <div className="glass-card p-12 flex flex-col items-center justify-center text-center">
          <div className="text-6xl text-white/10 mb-4">◈</div>
          <h2 className="text-xl font-medium text-white mb-2">No traces loaded</h2>
          <p className="text-textMuted max-w-md">
            Drag and drop Anvil trace JSON files anywhere on the page, or use the "Load Trace" button to begin visualizing agent runs.
          </p>
        </div>
      )}
    </div>
  );
}
