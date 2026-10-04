import { cn } from "@/lib/utils";

interface StatusBadgeProps {
  status: string;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const s = status.toLowerCase();

  let color = "bg-slate-800 text-slate-400 border-slate-700";

  if (s === "processed" || s === "success" || s === "active" || s === "true") {
    color = "bg-emerald-500/10 text-emerald-400 border-emerald-500/30";
  } else if (s === "pending" || s === "running") {
    color = "bg-amber-500/10 text-amber-400 border-amber-500/30";
  } else if (s === "failed" || s === "error" || s === "inactive" || s === "false") {
    color = "bg-rose-500/10 text-rose-400 border-rose-500/30";
  } else if (s === "partial") {
    color = "bg-blue-500/10 text-blue-400 border-blue-500/30";
  }

  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border capitalize",
        color,
        className
      )}
    >
      {status}
    </span>
  );
}
