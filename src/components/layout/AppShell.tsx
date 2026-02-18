import { Header } from './Header';

interface Props {
  children: React.ReactNode;
  showHeader?: boolean;
}

export function AppShell({ children, showHeader = true }: Props) {
  return (
    <div className="flex h-dvh flex-col bg-bg-page">
      {showHeader && <Header />}
      <main className="flex-1 overflow-auto">
        {children}
      </main>
      {/* Phase 2: <BottomNav /> */}
    </div>
  );
}
