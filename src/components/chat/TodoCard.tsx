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

export function TodoCard({ todos }: TodoCardProps) {
  const openTodos = todos.filter((t) => !t.done).length;
  const totalTodos = todos.length;

  return (
    <div className="my-2 max-w-[320px] rounded-xl border border-[#C8552D]/20 bg-[#FFF8F5] p-4 text-sm shadow-sm">
      <h3 className="mb-3 flex items-center gap-2 text-base font-bold text-[#2D2A26]">
        📋 Meine Todos
      </h3>
      <ul className="space-y-2.5">
        {todos.map((todo) => (
          <li key={todo.id} className="flex items-start gap-2.5">
            <span className="mt-0.5 text-base">
              {todo.done ? (
                <span className="text-green-600">✅</span>
              ) : (
                <span className="text-[#C8552D]">☐</span>
              )}
            </span>
            <div className="flex-grow min-w-0">
              <span
                className={`block ${
                  todo.done
                    ? 'text-[#8A8580] line-through'
                    : 'text-[#2D2A26] font-medium'
                }`}
              >
                {todo.text}
              </span>
              {todo.due_date && (
                <span className="text-xs text-[#8A8580]">
                  📅 {new Date(todo.due_date + 'T00:00:00').toLocaleDateString('de-DE', { day: '2-digit', month: '2-digit' })}
                </span>
              )}
            </div>
            {todo.priority === 'high' && !todo.done && (
              <span className="mt-0.5 rounded bg-red-100 px-1.5 py-0.5 text-xs font-medium text-red-700">
                Dringend
              </span>
            )}
          </li>
        ))}
      </ul>
      <div className="mt-3 flex items-center justify-between border-t border-[#C8552D]/10 pt-2">
        <span className="text-xs text-[#8A8580]">
          {openTodos} von {totalTodos} offen
        </span>
        <div className="h-1.5 w-20 rounded-full bg-[#E8E4E0]">
          <div
            className="h-full rounded-full bg-[#C8552D] transition-all"
            style={{ width: `${totalTodos > 0 ? ((totalTodos - openTodos) / totalTodos) * 100 : 0}%` }}
          />
        </div>
      </div>
    </div>
  );
}
