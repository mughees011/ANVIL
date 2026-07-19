import { useEffect, useState } from 'react';
import type { MemoryEntry } from '../types';

export function Memory() {
  const [agentName, setAgentName] = useState<string>('research_agent');
  const [collection, setCollection] = useState<'semantic' | 'episodic'>('semantic');
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL || "";

  useEffect(() => {
    if (!agentName) return;
    
    setLoading(true);
    setError(null);
    
    fetch(`${API_BASE}/api/agents/${agentName}/memory?collection=${collection}&limit=50`)
      .then(res => {
        if (!res.ok) throw new Error("Agent or collection not found");
        return res.json();
      })
      .then(data => {
        setMemories(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setMemories([]);
        setLoading(false);
      });
  }, [agentName, collection, API_BASE]);

  return (
    <div className="instrument-panel h-full flex flex-col">
      <div className="p-4 border-b border-line bg-line/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h3 className="font-heading text-lg font-medium text-ink">
          MEMORY_STORE
        </h3>
        <div className="flex items-center gap-4">
          <input 
            type="text" 
            value={agentName}
            onChange={e => setAgentName(e.target.value)}
            placeholder="Agent name..."
            className="bg-bgBase border border-line text-ink font-mono text-xs px-2 py-1 outline-none focus:border-data"
          />
          <select 
            value={collection}
            onChange={(e) => setCollection(e.target.value as any)}
            className="bg-bgBase border border-line text-ink font-mono text-xs px-2 py-1 outline-none focus:border-data"
          >
            <option value="semantic">Semantic</option>
            <option value="episodic">Episodic</option>
          </select>
        </div>
      </div>
      
      <div className="flex-1 overflow-auto p-4">
        {loading ? (
          <div className="p-16 text-center font-mono">
            <div className="text-4xl text-data mb-4 animate-pulse">...</div>
            <p className="text-inkMuted text-sm tracking-wide uppercase">Querying ChromaDB</p>
          </div>
        ) : error ? (
          <div className="p-16 text-center font-mono">
            <div className="text-4xl text-fail mb-4">!</div>
            <p className="text-fail/80 text-sm tracking-wide uppercase">{error}</p>
          </div>
        ) : memories.length === 0 ? (
          <div className="p-16 text-center font-mono">
            <div className="text-4xl text-data mb-4">[]</div>
            <p className="text-inkMuted text-sm tracking-wide uppercase">No memory indices loaded</p>
          </div>
        ) : (
          <div className="space-y-4">
            {memories.map(entry => (
              <div key={entry.id} className="bg-bgBase p-4 border border-line">
                <div className="font-sans text-sm text-ink mb-3">{entry.document}</div>
                <div className="grid grid-cols-[1fr_auto] gap-4 border-t border-line/50 pt-2 font-mono text-xs text-inkMuted">
                  <div className="truncate">ID: {entry.id}</div>
                  {entry.metadata?.timestamp && (
                    <div>{new Date(entry.metadata.timestamp).toLocaleString()}</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
