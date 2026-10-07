export default function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-dashed border-[var(--line-strong)] bg-[var(--surface)] p-8 text-center">
      <p className="text-3xl" aria-hidden>
        🔍
      </p>
      <h3 className="mt-2 text-lg font-bold text-[var(--ink)]">{title}</h3>
      <p className="mt-1 text-sm text-[var(--ink-muted)]">{description}</p>
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
