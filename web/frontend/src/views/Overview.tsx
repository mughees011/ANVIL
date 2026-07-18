import type { TraceData } from '../types';
import { useEffect, useState } from 'react';

interface OverviewProps {
  traces: TraceData[];
}

export function Overview({ traces }: OverviewProps) {
  const successfulRuns = traces.filter(t => t.final_status === 'success').length;
  const totalHeals = traces.reduce((acc, t) => acc + t.steps.reduce((sAcc, s) => sAcc + (s.retries || 0), 0), 0);
  const totalToolCalls = traces.reduce((acc, t) => acc + t.steps.reduce((sAcc, s) => sAcc + s.tool_calls.length, 0), 0);
  const memoryEntries = traces.length * 5; 

  const latestRun = traces.length > 0 ? traces[traces.length - 1] : null;
  const [pulse, setPulse] = useState(false);

  useEffect(() => {
    if (traces.length > 0) {
      setPulse(true);
      const t = setTimeout(() => setPulse(false), 500);
      return () => clearTimeout(t);
    }
  }, [traces.length]);

  return (
    <div className="space-y-6">
      {/* Signature Waveform Element */}
      <div className="instrument-panel p-4 h-32 flex flex-col justify-end overflow-hidden relative">
        <div className="mono-label absolute top-4 left-4">Signal_Trace</div>
        <div className="flex items-end h-full w-full gap-1 pt-8 opacity-80">
          {traces.length === 0 ? (
            <div className="w-full h-px bg-signal shadow-[0_0_8px_rgba(61,220,151,0.5)]"></div>
          ) : (
            <div className="w-full flex items-end gap-[2px]">
              {/* Generate waveform spikes based on latest run steps */}
              {latestRun?.steps.map((step, i) => {
                const height = step.retries > 0 ? 100 : (step.tool_calls.length * 20 + 20);
                const color = step.retries > 0 ? 'bg-retry shadow-[0_0_5px_rgba(232,163,61,0.5)]' : 
                             step.quality_check.rule_check === 'fail' ? 'bg-fail shadow-[0_0_5px_rgba(232,93,76,0.5)]' : 
                             'bg-signal shadow-[0_0_5px_rgba(61,220,151,0.5)]';
                return (
                  <div key={i} className="flex-1 flex flex-col justify-end h-full">
                    <div 
                      className={`w-full ${color} ${pulse ? 'animate-pulse' : ''} transition-all duration-300`} 
                      style={{ height: `${Math.min(height, 100)}%` }}
                    ></div>
                  </div>
                );
              })}
              <div className="flex-[3] h-px bg-signal shadow-[0_0_8px_rgba(61,220,151,0.5)]"></div>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="gauge-card relative">
          <div className="mono-label mb-2">SUCCESS_RUNS</div>
          <div className="font-mono text-4xl text-ink">{successfulRuns}</div>
          <div className="mt-4 flex gap-[2px]">
            {Array.from({length: 20}).map((_, i) => (
              <div key={i} className={`h-1 flex-1 ${i < successfulRuns % 20 ? 'bg-signal' : 'bg-line'}`}></div>
            ))}
          </div>
        </div>
        <div className="gauge-card relative">
          <div className="mono-label mb-2">SELF_HEALS</div>
          <div className="font-mono text-4xl text-ink">{totalHeals}</div>
          <div className="mt-4 flex gap-[2px]">
            {Array.from({length: 20}).map((_, i) => (
              <div key={i} className={`h-1 flex-1 ${i < totalHeals % 20 ? 'bg-retry' : 'bg-line'}`}></div>
            ))}
          </div>
        </div>
        <div className="gauge-card relative">
          <div className="mono-label mb-2">TOOL_CALLS</div>
          <div className="font-mono text-4xl text-ink">{totalToolCalls}</div>
          <div className="mt-4 flex gap-[2px]">
            {Array.from({length: 20}).map((_, i) => (
              <div key={i} className={`h-1 flex-1 ${i < (totalToolCalls/5) % 20 ? 'bg-signal' : 'bg-line'}`}></div>
            ))}
          </div>
        </div>
        <div className="gauge-card relative">
          <div className="mono-label mb-2">MEMORY_DATA</div>
          <div className="font-mono text-4xl text-ink">{memoryEntries}</div>
          <div className="mt-4 flex gap-[2px]">
            {Array.from({length: 20}).map((_, i) => (
              <div key={i} className={`h-1 flex-1 ${i < (memoryEntries/5) % 20 ? 'bg-data' : 'bg-line'}`}></div>
            ))}
          </div>
        </div>
      </div>

      {latestRun && (
        <div className="instrument-panel">
          <div className="flex items-center justify-between p-4 border-b border-line bg-line/20">
            <h3 className="font-heading text-lg font-medium text-ink flex items-center gap-2">
              LATEST_RUN
            </h3>
            <span className={`font-mono px-2 py-0.5 text-[10px] font-bold uppercase ${latestRun.final_status === 'success' ? 'bg-signal/20 text-signal border border-signal/50' : 'bg-fail/20 text-fail border border-fail/50'}`}>
              [{latestRun.final_status}]
            </span>
          </div>
          <div className="p-4 space-y-3 font-mono text-sm">
            <div className="grid grid-cols-[120px_1fr] border-b border-line pb-3">
              <span className="text-inkMuted">Task</span>
              <span className="text-ink font-sans">{latestRun.task}</span>
            </div>
            <div className="grid grid-cols-[120px_1fr] border-b border-line pb-3">
              <span className="text-inkMuted">Agent</span>
              <span className="text-ink">{latestRun.agent_name}</span>
            </div>
            <div className="grid grid-cols-[120px_1fr]">
              <span className="text-inkMuted">Run ID</span>
              <span className="text-inkMuted">{latestRun.run_id}</span>
            </div>
          </div>
        </div>
      )}

      {traces.length === 0 && (
        <div className="instrument-panel p-16 flex flex-col items-center justify-center text-center">
          <div className="font-mono text-signal animate-pulse mb-4">_</div>
          <h2 className="font-mono text-lg font-medium text-ink mb-2 tracking-widest">AWAITING SIGNAL</h2>
          <p className="font-mono text-xs text-inkMuted max-w-md">
            Drop a trace file, or run `anvil trace web` to connect a live agent.
          </p>
        </div>
      )}
    </div>
  );
}
