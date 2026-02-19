import { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';

interface Props {
  children: React.ReactNode;
  showSidebar?: boolean;
}

export function AppShell({ children, showSidebar = true }: Props) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  if (!showSidebar) {
    return (
      <div className="flex h-dvh flex-col bg-bg-page">
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    );
  }

  return (
    <div className="flex h-dvh overflow-hidden bg-bg-page">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
      />
      <div className="flex flex-1 flex-col relative">
        <TopBar />
        <main className="flex-1 overflow-auto px-10 pb-8 pt-2.5" style={{ scrollbarWidth: 'none' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
