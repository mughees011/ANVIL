export function Memory() {
  return (
    <div className="glass-card">
      <div className="p-4 border-b border-white/5 bg-black/20">
        <h3 className="text-lg font-medium text-white flex items-center gap-2">
          <span className="text-accentPurple">◆</span> Memory Store
        </h3>
      </div>
      <div className="p-8 text-center">
        <div className="text-4xl text-accentPurple/30 mb-4">◆</div>
        <p className="text-textMuted">Memory visualization will be populated here.</p>
        <p className="text-xs text-textMuted mt-2">Currently not included in the default trace schema.</p>
      </div>
    </div>
  );
}
