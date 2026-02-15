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
    <div className="max-w-[300px] rounded-[var(--radius-card)] bg-bg-card p-4 text-sm shadow-card">
      <h3 className="mb-3 font-bold text-text-strong">📋 Meine Todos</h3>
      <ul className="space-y-2">
        {todos.map((todo) => (
          <li key={todo.id} className="flex items-center gap-2">
            <span>{todo.done ? '☑' : '☐'}</span>
            <span
              className={`flex-grow ${
                todo.done ? 'text-text-muted line-through' : ''
              }`}
            >
              {todo.text}
            </span>
            {todo.due_date && (
              <span className="text-xs text-text-muted">{todo.due_date}</span>
            )}
            {todo.priority === 'high' && !todo.done && <span>⚠️</span>}
          </li>
        ))}
      </ul>
      <p className="mt-3 text-right text-xs text-text-muted">
        {openTodos} von {totalTodos} offen
      </p>
    </div>
  );
}
