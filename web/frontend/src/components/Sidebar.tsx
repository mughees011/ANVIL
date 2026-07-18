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
    <aside className="w-64 glass-panel flex flex-col h-screen fixed left-0 top-0">
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded bg-gradient-to-br from-accentCyan to-accentPurple flex items-center justify-center text-white font-bold text-lg shadow-[0_0_15px_rgba(34,211,238,0.4)]">
            ◈
          </div>
          <div className="font-bold text-xl tracking-wide text-white">ANVIL</div>
        </div>
        <div className="text-xs text-textMuted uppercase tracking-wider mt-2 font-medium">
          Agent Trace Dashboard
        </div>
      </div>
      
      <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
        {navItems.map(item => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full nav-item ${isActive ? 'active' : ''}`}
            >
              <Icon className="w-5 h-5" />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      
      <div className="p-4 border-t border-white/5 text-xs text-textMuted text-center">
        Drop .anvil/runs/*.json files anywhere
      </div>
    </aside>
  );
}
