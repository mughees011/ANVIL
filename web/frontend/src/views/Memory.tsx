export function Memory() {
  return (
    <div className="instrument-panel">
      <div className="p-4 border-b border-line bg-line/20">
        <h3 className="font-heading text-lg font-medium text-ink">
          MEMORY_STORE
        </h3>
      </div>
      <div className="p-16 text-center font-mono">
        <div className="text-4xl text-data mb-4">[]</div>
        <p className="text-inkMuted text-sm tracking-wide uppercase">No memory indices loaded</p>
        <p className="text-[10px] text-inkMuted mt-2">REQUIRES DB CONNECTION</p>
      </div>
    </div>
  );
}
