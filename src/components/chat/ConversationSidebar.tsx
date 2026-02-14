import { useState, useEffect } from 'react';
import { getConversations, deleteConversation } from '@/lib/api';
import type { Conversation } from '@/lib/types';

interface Props {
  currentId: string | null;
  onSelect: (id: string) => void;
  onNewChat: () => void;
  open: boolean;
  onClose: () => void;
}

export function ConversationSidebar({ currentId, onSelect, onNewChat, open, onClose }: Props) {
  const [conversations, setConversations] = useState<Conversation[]>([]);

  useEffect(() => {
    void getConversations().then(setConversations);
  }, [currentId]); // Refresh when conversation changes

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent triggering the selection click
    
    if (!confirm('Möchten Sie dieses Gespräch wirklich löschen?')) {
      return;
    }

    try {
      await deleteConversation(id);
      // Refresh the list
      const updated = await getConversations();
      setConversations(updated);
    } catch (error) {
      console.error('Fehler beim Löschen des Gesprächs:', error);
      alert('Gespräch konnte nicht gelöscht werden');
    }
  };

  function formatDate(iso: string) {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    if (diff < 86400000) return 'Heute';
    if (diff < 172800000) return 'Gestern';
    return d.toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' });
  }

  return (
    <>
      {/* Backdrop (mobile) */}
      {open && (
        <div
          className="fixed inset-0 z-30 bg-black/30 sm:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed left-0 top-0 z-40 flex h-full w-72 flex-col bg-bg-card border-r border-border
          transition-transform duration-200
          sm:relative sm:z-0 sm:translate-x-0
          ${open ? 'translate-x-0' : '-translate-x-full sm:translate-x-0'}
        `}
      >
        {/* Header */}
        <div className="flex h-14 items-center justify-between border-b border-border px-4 sm:h-16">
          <span className="text-sm font-semibold text-text-strong">Gespräche</span>
          <button
            type="button"
            onClick={() => { onNewChat(); onClose(); }}
            className="rounded-lg bg-primary px-3 py-1 text-xs font-medium text-white"
          >
            + Neu
          </button>
        </div>

        {/* List */}
        <div className="flex-1 overflow-y-auto">
          {conversations.length === 0 ? (
            <p className="px-4 py-8 text-center text-xs text-text-secondary">
              Noch keine Gespräche
            </p>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                className={`group relative border-b border-border/50 hover:bg-bg-subtle ${
                  c.id === currentId ? 'bg-bg-subtle' : ''
                }`}
              >
                <button
                  type="button"
                  onClick={() => { onSelect(c.id); onClose(); }}
                  className="w-full px-4 py-3 text-left"
                >
                  <div className="truncate text-sm font-medium text-text-default">
                    {c.title || 'Neues Gespräch'}
                  </div>
                  <div className="mt-0.5 text-xs text-text-secondary">
                    {formatDate(c.updated_at)}
                  </div>
                </button>
                <button
                  type="button"
                  onClick={(e) => handleDelete(c.id, e)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1.5 text-text-secondary opacity-0 transition-opacity hover:bg-bg-subtle-hover hover:text-danger group-hover:opacity-100"
                  title="Gespräch löschen"
                >
                  🗑️
                </button>
              </div>
            ))
          )}
        </div>
      </aside>
    </>
  );
}