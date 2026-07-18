import { LayoutDashboard, List, GitCommit, Database, Workflow } from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onViewChange: (view: string) => void;
}

export function Sidebar({ currentView, onViewChange }: SidebarProps) {
  const navItems = [
    { id: 'overview', icon: LayoutDashboard, label: 'Overview' },
    { id: 'runs', icon: List, label: 'Runs' },
    { id: 'plan', icon: GitCommit, label: 'Plan & Trace' },
    { id: 'memory', icon: Database, label: 'Memory' },
    { id: 'arch', icon: Workflow, label: 'Architecture' },
  ];

  return (
    <aside className="w-64 instrument-panel flex flex-col h-screen fixed left-0 top-0 border-y-0 border-l-0">
      <div className="p-6 border-b border-line">
        <div className="flex items-center gap-3">
          <div className="text-signal flex items-center justify-center">
            {/* Flat line-drawn waveform/anvil motif */}
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="square" strokeLinejoin="miter">
              <path d="M2 12h4l3-7 5 14 3-7h5" />
            </svg>
          </div>
          <div className="font-heading font-bold text-xl tracking-wide text-ink">ANVIL</div>
        </div>
        <div className="font-mono text-[10px] text-inkMuted uppercase tracking-wider mt-2">
          Trace Instrument // v1.0
        </div>
      </div>
      
      <nav className="flex-1 py-4 flex flex-col space-y-1 overflow-y-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full nav-item ${isActive ? 'active' : 'border-l-2 border-transparent'}`}
            >
              <Icon className="w-4 h-4" />
              <span className="font-sans text-sm">{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-line font-mono text-[10px] text-inkMuted leading-tight">
        AWAITING SIGNAL...<br/>
        DROP .JSON TO READ
      </div>
    </aside>
  );
}
