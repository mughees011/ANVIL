import type { TraceData } from '../types';

interface PlanAndTraceProps {
  traces: TraceData[];
  selectedRunId: string | null;
}

export function PlanAndTrace({ traces, selectedRunId }: PlanAndTraceProps) {
  const selectedRun = traces.find(t => t.run_id === selectedRunId);

  if (!selectedRun) {
    return (
      <div className="glass-card p-12 flex flex-col items-center justify-center text-center">
        <div className="text-4xl text-white/10 mb-4">▦</div>
        <h2 className="text-xl font-medium text-white mb-2">No run selected</h2>
        <p className="text-textMuted">Select a run from the Runs tab to view its plan and execution trace.</p>
      </div>
    );
  }

  return (
    <div className="glass-card overflow-hidden">
      <div className="p-4 border-b border-white/5 bg-black/20">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-medium text-white flex items-center gap-2">
            <span className="text-accentCyan">▦</span> Execution Plan & Trace
          </h3>
          <span className="text-xs font-mono text-textMuted bg-black/30 px-2 py-1 rounded">{selectedRun.run_id}</span>
        </div>
        <div className="text-sm text-textPrimary font-medium border-l-2 border-accentCyan pl-3 py-1 bg-accentCyan/5">
          {selectedRun.task}
        </div>
      </div>
      
      <div className="p-6 space-y-6">
        {selectedRun.plan.map((planStep, idx) => {
          const executionStep = selectedRun.steps.find(s => s.step_id === planStep.step_id);
          
          return (
            <div key={planStep.step_id} className="relative pl-6 border-l border-white/10 pb-2 last:border-transparent">
              <div className="absolute w-3 h-3 rounded-full bg-bgPanel border-2 border-white/20 -left-[6.5px] top-1.5" />
              
              <div className="mb-1 flex items-center gap-2">
                <span className="text-xs font-bold text-accentCyan">STEP {idx + 1}</span>
                <h4 className="font-medium text-white">{planStep.description}</h4>
                {planStep.status === 'success' && <span className="text-accentGreen text-xs">✓</span>}
                {planStep.status === 'retried' && <span className="text-accentAmber text-xs">↻</span>}
                {planStep.status === 'failed' && <span className="text-red-500 text-xs">✗</span>}
              </div>
              
              {executionStep && (
                <div className="mt-3 space-y-3">
                  {executionStep.tool_calls.map((tc, tcIdx) => (
                    <div key={tcIdx} className="bg-black/40 rounded-lg p-3 border border-white/5 font-mono text-xs">
                      <div className="text-textMuted mb-2">
                        <span className="text-white">call</span> {tc.tool}(...)
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <div className="text-[10px] text-textMuted uppercase mb-1">Input</div>
                          <pre className="text-accentPurple/80 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(tc.input, null, 2)}</pre>
                        </div>
                        <div>
                          <div className="text-[10px] text-textMuted uppercase mb-1">Output</div>
                          <pre className="text-accentGreen/80 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(tc.output, null, 2)}</pre>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {(executionStep.retries > 0 || executionStep.quality_check.rule_check === 'fail') && (
                    <div className="text-xs text-accentAmber bg-accentAmber/10 px-3 py-2 rounded flex items-center gap-2">
                      <span>↻</span> Quality check failed. Retries: {executionStep.retries}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
