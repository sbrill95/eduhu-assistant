import { useState, useRef } from 'react';
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
  const [newText, setNewText] = useState('');
  const [newDate, setNewDate] = useState('');
  const [adding, setAdding] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const openTodos = todos.filter((t) => !t.done).length;
  const totalTodos = todos.length;

  async function toggleTodo(todoId: string, currentDone: boolean) {
    const teacher = getSession();
    if (!teacher) return;
    setTodos((prev) => prev.map((t) => t.id === todoId ? { ...t, done: !currentDone } : t));
    try {
      await fetch(`${API_BASE}/api/todos/${todoId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json', 'X-Teacher-ID': teacher.teacher_id },
        body: JSON.stringify({ done: !currentDone }),
      });
    } catch {
      setTodos((prev) => prev.map((t) => t.id === todoId ? { ...t, done: currentDone } : t));
    }
  }

  async function addTodo() {
    const text = newText.trim();
    if (!text) return;
    const teacher = getSession();
    if (!teacher) return;

    setAdding(true);
    try {
      const resp = await fetch(`${API_BASE}/api/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Teacher-ID': teacher.teacher_id },
        body: JSON.stringify({ text, ...(newDate ? { due_date: newDate } : {}) }),
      });
      if (resp.ok) {
        const created = await resp.json();
        setTodos((prev) => [...prev, { id: created.id, text: created.text, done: false, due_date: created.due_date, priority: created.priority || 'normal' }]);
        setNewText('');
        setNewDate('');
      }
    } catch { /* ignore */ }
    setAdding(false);
  }

  return (
    <div className="my-2 max-w-[340px] overflow-hidden rounded-xl border border-[#D9D3CD] bg-white text-sm shadow-sm">
      <div className="bg-[#F5F0EB] px-4 py-2.5">
        <h3 className="flex items-center gap-2 text-base font-bold text-[#2D2018]">
          📋 Meine Todos
        </h3>
      </div>
      <ul className="space-y-0 divide-y divide-[#D9D3CD] px-4">
        {todos.length === 0 && (
          <li className="py-3 text-center text-[#9E9A96]">Keine Todos vorhanden 🎉</li>
        )}
        {todos.map((todo) => (
          <li key={todo.id} className="flex items-start gap-2.5 py-2.5">
            <button
              type="button"
              onClick={() => toggleTodo(todo.id, todo.done)}
              className="mt-0.5 text-base transition-transform hover:scale-110 active:scale-95 cursor-pointer select-none"
              aria-label={todo.done ? `${todo.text} als offen markieren` : `${todo.text} als erledigt markieren`}
            >
              {todo.done ? '✅' : <span className="text-[#C8552D]">☐</span>}
            </button>
            <div className="flex-grow min-w-0">
              <span className={`block transition-all ${todo.done ? 'text-[#9E9A96] line-through' : 'text-[#2D2018] font-medium'}`}>
                {todo.text}
              </span>
              {todo.due_date && (
                <span className="text-xs text-[#6B6360]">
                  📅 {new Date(todo.due_date + 'T00:00:00').toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })}
                </span>
              )}
            </div>
            {todo.priority === 'high' && !todo.done && (
              <span className="mt-0.5 shrink-0 rounded-full bg-[#F2A8A0] px-2 py-0.5 text-xs font-semibold text-white">
                Dringend
              </span>
            )}
          </li>
        ))}
      </ul>

      {/* Add new todo */}
      <div className="border-t border-[#D9D3CD] px-4 py-2">
        <form onSubmit={(e) => { e.preventDefault(); void addTodo(); }} className="flex items-center gap-2">
          <span className="text-[#C8552D] font-bold">＋</span>
          <input
            ref={inputRef}
            type="text"
            value={newText}
            onChange={(e) => setNewText(e.target.value)}
            placeholder="Neues Todo..."
            disabled={adding}
            className="flex-grow bg-transparent text-sm text-[#3A3530] placeholder:text-[#9E9A96] outline-none"
          />
          <input
            type="date"
            value={newDate}
            onChange={(e) => setNewDate(e.target.value)}
            disabled={adding}
            className="w-8 shrink-0 cursor-pointer bg-transparent text-xs text-[#6B6360] opacity-60 hover:opacity-100 [&::-webkit-calendar-picker-indicator]:cursor-pointer"
            title="Fälligkeitsdatum"
          />
          {newText.trim() && (
            <button
              type="submit"
              disabled={adding}
              className="shrink-0 rounded-full bg-[#C8552D] px-2.5 py-0.5 text-xs font-medium text-white hover:bg-[#A8461F] disabled:opacity-50"
            >
              {adding ? '...' : '＋'}
            </button>
          )}
        </form>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between border-t border-[#D9D3CD] bg-[#F5F0EB] px-4 py-2">
        <span className="text-xs font-medium text-[#6B6360]">
          {openTodos} von {totalTodos} offen
        </span>
        <div className="h-1.5 w-20 rounded-full bg-white">
          <div
            className="h-full rounded-full bg-[#4A8C5C] transition-all"
            style={{ width: `${totalTodos > 0 ? ((totalTodos - openTodos) / totalTodos) * 100 : 0}%` }}
          />
        </div>
      </div>
    </div>
  );
}
