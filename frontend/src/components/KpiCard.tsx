import { useI18n } from "../i18n/I18nContext";

interface KpiCardProps {
  label: string;
  value: string;
  hint?: string | null;
  change?: number | null;
}

export function KpiCard({ label, value, hint, change }: KpiCardProps) {
  const { t } = useI18n();
  const hasChange = typeof change === "number";
  const positive = (change ?? 0) >= 0;

  return (
    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className="mt-2 text-3xl font-semibold text-slate-900">{value}</p>
      {hasChange && (
        <p className={`mt-2 text-sm font-medium ${positive ? "text-emerald-600" : "text-red-600"}`}>
          {positive ? "▲" : "▼"} {Math.abs(change as number).toFixed(1)}%{" "}
          <span className="font-normal text-slate-400">{t.kpi.vsPrevious}</span>
        </p>
      )}
      {hint && !hasChange && <p className="mt-2 text-sm text-slate-400">{hint}</p>}
    </article>
  );
}
