export function Architecture() {
  return (
    <div className="space-y-6">
      <div className="instrument-panel p-8 flex items-center justify-center min-h-[400px]">
        <svg className="w-full max-w-3xl" viewBox="0 0 620 440">
          <defs>
            <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 Z" fill="#262A2E"/>
            </marker>
            <marker id="arrowhead-active" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 Z" fill="#3DDC97"/>
            </marker>
          </defs>
          {/* Task input */}
          <text x="90" y="38" fill="#8A8F94" fontSize="12" fontFamily="IBM Plex Mono" textAnchor="end">TASK_IN</text>
          <path d="M 110 42 L 190 42" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          
          {/* Planner */}
          <rect x="200" y="20" width="200" height="44" fill="#0A0B0C" stroke="#3DDC97" strokeWidth="1" rx="2"/>
          <text x="300" y="47" fill="#E8E6E1" fontSize="15" fontFamily="Space Grotesk" textAnchor="middle" fontWeight="500">PLANNER</text>
          
          {/* Memory recall */}
          <path d="M 80 90 L 190 55" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="100" y="62" fill="#8B7FD1" fontSize="10" fontFamily="IBM Plex Mono">RECALL</text>
          
          {/* Plan arrow */}
          <path d="M 300 64 L 300 100" stroke="#3DDC97" strokeWidth="2" markerEnd="url(#arrowhead-active)"/>
          
          {/* Executor */}
          <rect x="200" y="110" width="200" height="44" fill="#0A0B0C" stroke="#262A2E" strokeWidth="1" rx="2"/>
          <text x="300" y="137" fill="#E8E6E1" fontSize="15" fontFamily="Space Grotesk" textAnchor="middle" fontWeight="500">EXECUTOR</text>
          
          {/* Tool registry */}
          <path d="M 500 140 L 410 140" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="460" y="132" fill="#8A8F94" fontSize="10" fontFamily="IBM Plex Mono">TOOLS_REG</text>
          
          {/* Result arrow */}
          <path d="M 300 154 L 300 190" stroke="#3DDC97" strokeWidth="2" markerEnd="url(#arrowhead-active)"/>
          
          {/* QualityEnforcer */}
          <rect x="170" y="200" width="260" height="44" fill="#0A0B0C" stroke="#262A2E" strokeWidth="1" rx="2"/>
          <text x="300" y="227" fill="#E8E6E1" fontSize="15" fontFamily="Space Grotesk" textAnchor="middle" fontWeight="500">QUALITY_ENFORCER</text>
          
          {/* Pass path */}
          <path d="M 170 222 L 110 222 L 110 360 L 200 360" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="80" y="295" fill="#3DDC97" fontSize="10" fontFamily="IBM Plex Mono">PASS</text>
          
          {/* Fail path */}
          <path d="M 430 222 L 490 222 L 490 310 L 400 310" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="510" y="270" fill="#E85D4C" fontSize="10" fontFamily="IBM Plex Mono">FAIL</text>
          
          {/* SelfHealingEngine */}
          <rect x="200" y="290" width="200" height="44" fill="#0A0B0C" stroke="#E8A33D" strokeWidth="1" rx="2"/>
          <text x="300" y="317" fill="#E8E6E1" fontSize="15" fontFamily="Space Grotesk" textAnchor="middle" fontWeight="500">SELF_HEALING_ENGINE</text>
          
          {/* Retry up */}
          <path d="M 300 290 L 300 255" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="315" y="280" fill="#E8A33D" fontSize="10" fontFamily="IBM Plex Mono">RETRY</text>
          
          {/* Re-plan loop */}
          <path d="M 200 310 L 110 310 L 110 50 L 190 50" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="70" y="180" fill="#E8A33D" fontSize="10" fontFamily="IBM Plex Mono">RE-PLAN</text>
          
          {/* Next step */}
          <path d="M 300 350 L 300 390" stroke="#262A2E" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="315" y="380" fill="#8A8F94" fontSize="10" fontFamily="IBM Plex Mono">NEXT</text>
          
          {/* Done */}
          <text x="340" y="405" fill="#E8E6E1" fontSize="12" fontFamily="IBM Plex Mono">HALT</text>
        </svg>
      </div>

      <div className="instrument-panel p-6">
        <h3 className="font-heading text-lg font-medium text-ink mb-4">MODULE_REF</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-bgBase p-4 border border-signal">
            <h4 className="font-mono text-signal text-[10px] tracking-widest mb-2">MOD::PLANNER</h4>
            <p className="font-sans text-xs text-inkMuted">Takes a Task + Tools + Memory → produces a structured Plan.</p>
          </div>
          <div className="bg-bgBase p-4 border border-line">
            <h4 className="font-mono text-ink text-[10px] tracking-widest mb-2">MOD::EXECUTOR</h4>
            <p className="font-sans text-xs text-inkMuted">Runs Step by Step, resolves Tools, captures IO blocks.</p>
          </div>
          <div className="bg-bgBase p-4 border border-line">
            <h4 className="font-mono text-ink text-[10px] tracking-widest mb-2">MOD::QUALITY_ENF</h4>
            <p className="font-sans text-xs text-inkMuted">Deterministic rule checks + optional LLM-graded rubric gating.</p>
          </div>
          <div className="bg-bgBase p-4 border border-retry">
            <h4 className="font-mono text-retry text-[10px] tracking-widest mb-2">MOD::HEAL_ENGINE</h4>
            <p className="font-sans text-xs text-inkMuted">Same-step retry for exceptions, partial re-plan for QC failures.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
