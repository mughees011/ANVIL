import type { TraceData } from '../types';

interface PlanAndTraceProps {
  traces: TraceData[];
  selectedRunId: string | null;
}

export function PlanAndTrace({ traces, selectedRunId }: PlanAndTraceProps) {
  const selectedRun = traces.find(t => t.run_id === selectedRunId);

  if (!selectedRun) {
    return (
      <div className="instrument-panel p-16 flex flex-col items-center justify-center text-center">
        <div className="font-mono text-signal mb-4">_</div>
        <h2 className="font-mono text-lg font-medium text-ink mb-2 uppercase tracking-widest">NO TARGET SPECIFIED</h2>
        <p className="font-mono text-xs text-inkMuted">Select a run from the Runs tab to view execution sequence.</p>
      </div>
    );
  }

  return (
    <div className="instrument-panel overflow-hidden">
      <div className="p-4 border-b border-line bg-line/20">
        <div className="flex justify-between items-center mb-2">
          <h3 className="font-heading text-lg font-medium text-ink">
            EXECUTION_TRACE
          </h3>
          <span className="font-mono text-[10px] text-inkMuted border border-line px-1.5 py-0.5">{selectedRun.run_id}</span>
        </div>
        <div className="font-sans text-sm text-ink font-medium border-l-[3px] border-signal pl-3 py-1">
          {selectedRun.task}
        </div>
      </div>
      
      <div className="p-6 space-y-6">
        {selectedRun.plan.map((planStep, idx) => {
          const executionStep = selectedRun.steps.find(s => s.step_id === planStep.step_id);
          
          return (
            <div key={planStep.step_id} className="relative pl-6 border-l border-line pb-4 last:border-transparent">
              <div className="absolute w-2 h-2 rounded-sm bg-bgPanel border border-line -left-[4.5px] top-1.5" />
              
              <div className="mb-2 flex items-center gap-3">
                <span className="font-mono text-[10px] font-bold text-signal">STEP_{idx + 1}</span>
                <h4 className="font-sans font-medium text-ink">{planStep.description}</h4>
                {planStep.status === 'success' && <span className="text-signal font-mono text-xs">[PASS]</span>}
                {planStep.status === 'retried' && <span className="text-retry font-mono text-xs">[RETRY]</span>}
                {planStep.status === 'failed' && <span className="text-fail font-mono text-xs">[FAIL]</span>}
              </div>
              
              {executionStep && (
                <div className="mt-3 space-y-3">
                  {executionStep.tool_calls.map((tc, tcIdx) => (
                    <div key={tcIdx} className="bg-bgBase p-3 border border-line font-mono text-xs">
                      <div className="text-inkMuted mb-2">
                        <span className="text-ink">&gt; CALL</span> {tc.tool}()
                      </div>
                      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 border-t border-line/50 pt-2 mt-2">
                        <div>
                          <div className="text-[10px] text-inkMuted uppercase mb-1">Input_Args</div>
                          <pre className="text-ink/80 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(tc.input, null, 2)}</pre>
                        </div>
                        <div>
                          <div className="text-[10px] text-inkMuted uppercase mb-1">Return_Data</div>
                          <pre className="text-signal/90 overflow-x-auto whitespace-pre-wrap">{JSON.stringify(tc.output, null, 2)}</pre>
                        </div>
                      </div>
                    </div>
                  ))}
                  
                  {(executionStep.retries > 0 || executionStep.quality_check.rule_check === 'fail') && (
                    <div className="font-mono text-xs text-retry border border-retry/50 px-3 py-2 flex items-center gap-2">
                      <span>!</span> QC_FAIL. RETRIES_LOGGED: {executionStep.retries}
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
