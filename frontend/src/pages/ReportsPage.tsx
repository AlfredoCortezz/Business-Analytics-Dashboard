import { api } from "../api/client";
import { ErrorState, LoadingState } from "../components/states/States";
import { useFilters } from "../context/FiltersContext";
import { useAsync } from "../hooks/useAsync";
import { useI18n } from "../i18n/I18nContext";

export function ReportsPage() {
  const { t } = useI18n();
  const { filters, query } = useFilters();
  const summary = useAsync(() => api.summary(query), [JSON.stringify(filters)]);

  const download = (url: string) => {
    window.location.href = url;
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{t.reports.title}</h2>
        <p className="mt-1 text-sm text-slate-500">{t.reports.subtitle}</p>
      </div>

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700">{t.reports.period}</h3>
        {summary.loading ? (
          <LoadingState />
        ) : summary.error ? (
          <ErrorState message={summary.error} onRetry={summary.reload} />
        ) : (
          <div className="mt-3 grid gap-4 sm:grid-cols-3">
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">{t.filters.dateFrom}</p>
              <p className="font-medium text-slate-800">{summary.data?.period.date_from ?? "—"}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">{t.filters.dateTo}</p>
              <p className="font-medium text-slate-800">{summary.data?.period.date_to ?? "—"}</p>
            </div>
            <div className="rounded-lg bg-slate-50 p-3">
              <p className="text-xs text-slate-500">{t.kpi.sales}</p>
              <p className="font-medium text-slate-800">{summary.data?.total_sales ?? 0}</p>
            </div>
          </div>
        )}

        <div className="mt-5 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => download(api.reportCsvUrl(query))}
            className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
          >
            {t.reports.downloadCsv}
          </button>
          <button
            type="button"
            onClick={() => download(api.reportPdfUrl(query))}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100"
          >
            {t.reports.downloadPdf}
          </button>
        </div>
        <p className="mt-3 text-xs text-slate-400">{t.reports.includes}</p>
      </section>
    </div>
  );
}
