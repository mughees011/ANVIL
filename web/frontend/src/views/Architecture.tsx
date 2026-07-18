export function Architecture() {
  return (
    <div className="space-y-6">
      <div className="glass-card p-8 flex items-center justify-center min-h-[400px]">
        <svg className="w-full max-w-3xl" viewBox="0 0 620 440">
          <defs>
            <marker id="arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 Z" fill="rgba(255,255,255,0.2)"/>
            </marker>
            <marker id="arrowhead-active" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
              <path d="M0,0 L8,3 L0,6 Z" fill="#22D3EE"/>
            </marker>
          </defs>
          {/* Task input */}
          <text x="90" y="38" fill="#64748B" fontSize="14" textAnchor="end">Task</text>
          <path d="M 110 42 L 190 42" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          
          {/* Planner */}
          <rect x="200" y="20" width="200" height="44" fill="rgba(34,211,238,0.1)" stroke="#22D3EE" strokeWidth="1" rx="6"/>
          <text x="300" y="47" fill="#F1F5F9" fontSize="15" textAnchor="middle" fontWeight="500">Planner</text>
          
          {/* Memory recall */}
          <path d="M 80 90 L 190 55" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="100" y="62" fill="#64748B" fontSize="12">recall</text>
          
          {/* Plan arrow */}
          <path d="M 300 64 L 300 100" stroke="#22D3EE" strokeWidth="2" markerEnd="url(#arrowhead-active)"/>
          
          {/* Executor */}
          <rect x="200" y="110" width="200" height="44" fill="rgba(168,85,247,0.1)" stroke="#A855F7" strokeWidth="1" rx="6"/>
          <text x="300" y="137" fill="#F1F5F9" fontSize="15" textAnchor="middle" fontWeight="500">Executor</text>
          
          {/* Tool registry */}
          <path d="M 500 140 L 410 140" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="460" y="132" fill="#64748B" fontSize="12">tools</text>
          
          {/* Result arrow */}
          <path d="M 300 154 L 300 190" stroke="#22D3EE" strokeWidth="2" markerEnd="url(#arrowhead-active)"/>
          
          {/* QualityEnforcer */}
          <rect x="170" y="200" width="260" height="44" fill="rgba(34,197,94,0.1)" stroke="#22C55E" strokeWidth="1" rx="6"/>
          <text x="300" y="227" fill="#F1F5F9" fontSize="15" textAnchor="middle" fontWeight="500">QualityEnforcer</text>
          
          {/* Pass path */}
          <path d="M 170 222 L 110 222 L 110 360 L 200 360" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="80" y="295" fill="#22C55E" fontSize="12">pass</text>
          
          {/* Fail path */}
          <path d="M 430 222 L 490 222 L 490 310 L 400 310" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="510" y="270" fill="#EF4444" fontSize="12">fail</text>
          
          {/* SelfHealingEngine */}
          <rect x="200" y="290" width="200" height="44" fill="rgba(245,158,11,0.1)" stroke="#F59E0B" strokeWidth="1" rx="6"/>
          <text x="300" y="317" fill="#F1F5F9" fontSize="15" textAnchor="middle" fontWeight="500">SelfHealingEngine</text>
          
          {/* Retry up */}
          <path d="M 300 290 L 300 255" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="315" y="280" fill="#F59E0B" fontSize="12">retry</text>
          
          {/* Re-plan loop */}
          <path d="M 200 310 L 110 310 L 110 50 L 190 50" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)" fill="none"/>
          <text x="70" y="180" fill="#F59E0B" fontSize="12">re-plan</text>
          
          {/* Next step */}
          <path d="M 300 350 L 300 390" stroke="rgba(255,255,255,0.2)" strokeWidth="2" markerEnd="url(#arrowhead)"/>
          <text x="315" y="380" fill="#64748B" fontSize="12">next</text>
          
          {/* Done */}
          <text x="340" y="405" fill="#F1F5F9" fontSize="14">Done</text>
        </svg>
      </div>

      <div className="glass-card p-6">
        <h3 className="text-lg font-medium text-white mb-4">Component Reference</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-black/20 p-4 rounded-lg border border-accentCyan/20">
            <h4 className="text-accentCyan font-medium mb-1">Planner</h4>
            <p className="text-xs text-textMuted">Takes a Task + available Tools + Memory → produces a structured Plan.</p>
          </div>
          <div className="bg-black/20 p-4 rounded-lg border border-accentPurple/20">
            <h4 className="text-accentPurple font-medium mb-1">Executor</h4>
            <p className="text-xs text-textMuted">Runs one Step at a time, resolves Tool(s), calls them, captures results.</p>
          </div>
          <div className="bg-black/20 p-4 rounded-lg border border-accentGreen/20">
            <h4 className="text-accentGreen font-medium mb-1">QualityEnforcer</h4>
            <p className="text-xs text-textMuted">Rule-based checks + optional LLM-graded rubric checks.</p>
          </div>
          <div className="bg-black/20 p-4 rounded-lg border border-accentAmber/20">
            <h4 className="text-accentAmber font-medium mb-1">SelfHealingEngine</h4>
            <p className="text-xs text-textMuted">On failure: same-step retry for exceptions, partial re-plan for quality failures.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
