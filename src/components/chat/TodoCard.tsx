import { useState } from 'react';
import { getSession } from '@/lib/auth';
import { API_BASE } from '@/lib/api';

interface TodoItem {
  id: string;
  text: string;
  done: boolean;
  due_date?: string;
  priority?: string;
}

interface TodoCardProps {
  todos: TodoItem[];
}

export function TodoCard({ todos: initialTodos }: TodoCardProps) {
  const [todos, setTodos] = useState(initialTodos);

  const openTodos = todos.filter((t) => !t.done).length;
  const totalTodos = todos.length;

  async function toggleTodo(todoId: string, currentDone: boolean) {
    const teacher = getSession();
    if (!teacher) return;

    // Optimistic update
    setTodos((prev) =>
      prev.map((t) =>
        t.id === todoId ? { ...t, done: !currentDone } : t
      )
    );

    try {
      await fetch(`${API_BASE}/api/todos/${todoId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'X-Teacher-ID': teacher.teacher_id,
        },
        body: JSON.stringify({ done: !currentDone }),
      });
    } catch {
      // Revert on error
      setTodos((prev) =>
        prev.map((t) =>
          t.id === todoId ? { ...t, done: currentDone } : t
        )
      );
    }
  }

  return (
    <div className="my-2 max-w-[320px] overflow-hidden rounded-xl border border-[var(--color-sage)]/40 bg-[var(--color-sage-soft)] text-sm shadow-sm">
      <div className="bg-[var(--color-sage)]/30 px-4 py-2.5">
        <h3 className="flex items-center gap-2 text-base font-bold text-[#2D2A26]">
          📋 Meine Todos
        </h3>
      </div>
      <ul className="space-y-0 divide-y divide-[var(--color-sage)]/20 px-4">
        {todos.map((todo) => (
          <li key={todo.id} className="flex items-start gap-2.5 py-2.5">
            <button
              type="button"
              onClick={() => toggleTodo(todo.id, todo.done)}
              className="mt-0.5 text-base transition-transform hover:scale-125 active:scale-95 cursor-pointer"
              title={todo.done ? 'Als offen markieren' : 'Als erledigt markieren'}
            >
              {todo.done ? (
                <span className="text-[var(--color-success)]">✅</span>
              ) : (
                <span className="text-[var(--color-primary)]">☐</span>
              )}
            </button>
            <div className="flex-grow min-w-0">
              <span
                className={`block transition-all ${
                  todo.done
                    ? 'text-[var(--color-text-muted)] line-through'
                    : 'text-[var(--color-text-strong)] font-medium'
                }`}
              >
                {todo.text}
              </span>
              {todo.due_date && (
                <span className="text-xs text-[var(--color-text-secondary)]">
                  📅 {new Date(todo.due_date + 'T00:00:00').toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })}
                </span>
              )}
            </div>
            {todo.priority === 'high' && !todo.done && (
              <span className="mt-0.5 rounded-full bg-[var(--color-salmon)] px-2 py-0.5 text-xs font-semibold text-white">
                Dringend
              </span>
            )}
          </li>
        ))}
      </ul>
      <div className="flex items-center justify-between border-t border-[var(--color-sage)]/30 bg-[var(--color-sage)]/15 px-4 py-2">
        <span className="text-xs font-medium text-[var(--color-text-secondary)]">
          {openTodos} von {totalTodos} offen
        </span>
        <div className="h-1.5 w-20 rounded-full bg-white/60">
          <div
            className="h-full rounded-full bg-[var(--color-success)] transition-all"
            style={{ width: `${totalTodos > 0 ? ((totalTodos - openTodos) / totalTodos) * 100 : 0}%` }}
          />
        </div>
      </div>
    </div>
  );
}
