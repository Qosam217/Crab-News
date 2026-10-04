import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  color?: "rose" | "amber" | "emerald" | "blue" | "purple";
}

const COLOR_MAP = {
  rose: {
    bg: "bg-rose-500/10 border-rose-500/20",
    icon: "text-rose-400 bg-rose-500/15",
  },
  amber: {
    bg: "bg-amber-500/10 border-amber-500/20",
    icon: "text-amber-400 bg-amber-500/15",
  },
  emerald: {
    bg: "bg-emerald-500/10 border-emerald-500/20",
    icon: "text-emerald-400 bg-emerald-500/15",
  },
  blue: {
    bg: "bg-blue-500/10 border-blue-500/20",
    icon: "text-blue-400 bg-blue-500/15",
  },
  purple: {
    bg: "bg-purple-500/10 border-purple-500/20",
    icon: "text-purple-400 bg-purple-500/15",
  },
};

export function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = "rose",
}: StatsCardProps) {
  const styles = COLOR_MAP[color];

  return (
    <div
      className={cn(
        "p-5 rounded-xl bg-slate-900/80 border border-slate-800 transition-all hover:border-slate-700 relative overflow-hidden",
        styles.bg
      )}
    >
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
          {title}
        </span>
        <div className={cn("p-2 rounded-lg", styles.icon)}>
          <Icon className="w-4 h-4" />
        </div>
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold text-white tracking-tight">{value}</div>
        {(subtitle || trend) && (
          <div className="mt-1 flex items-center gap-2 text-xs text-slate-400">
            {trend && (
              <span
                className={cn(
                  "font-medium",
                  trend.isPositive ? "text-emerald-400" : "text-rose-400"
                )}
              >
                {trend.isPositive ? "↑" : "↓"} {trend.value}
              </span>
            )}
            {subtitle && <span>{subtitle}</span>}
          </div>
        )}
      </div>
    </div>
  );
}
