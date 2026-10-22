import { useState } from "react";
import { api } from "../api/client";
import { CategoryBarChart, SalesTrendChart, TopProductsChart } from "../components/charts/Charts";
import { KpiCard } from "../components/KpiCard";
import { EmptyState, ErrorState, LoadingState } from "../components/states/States";
import { useFilters } from "../context/FiltersContext";
import { useAsync } from "../hooks/useAsync";
import { useI18n } from "../i18n/I18nContext";

const money = (value: number) =>
  new Intl.NumberFormat(undefined, { maximumFractionDigits: 2 }).format(value);

export function DashboardPage() {
  const { t } = useI18n();
  const { filters, query } = useFilters();
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const key = JSON.stringify(filters);
  const summary = useAsync(() => api.summary(query), [key]);
  const timeseries = useAsync(() => api.timeseries(query), [key]);
  const categories = useAsync(() => api.categories(query), [key]);
  const products = useAsync(() => api.products(query, 8), [key]);

  const loading = summary.loading || timeseries.loading || categories.loading || products.loading;
  const error = summary.error || timeseries.error || categories.error || products.error;

  const runDemoAction = async (action: "seed" | "reset") => {
    setBusy(true);
    setNotice(null);
    try {
      const response = action === "seed" ? await api.seedDemo() : await api.resetDemo();
      setNotice(response.message);
      summary.reload();
      timeseries.reload();
      categories.reload();
      products.reload();
    } catch (err) {
      setNotice((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  if (loading) return <LoadingState />;
  if (error) return <ErrorState message={error} onRetry={summary.reload} />;

  const data = summary.data!;
  const hasData = data.total_sales > 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="text-xl font-semibold text-slate-900">{t.dashboard.title}</h2>
        <div className="flex gap-2">
          <button
            type="button"
            disabled={busy}
            onClick={() => runDemoAction("seed")}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            {t.dashboard.loadDemo}
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => runDemoAction("reset")}
            className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 disabled:opacity-50"
          >
            {t.dashboard.resetDemo}
          </button>
        </div>
      </div>

      {notice && (
        <p role="status" className="rounded-lg border border-brand-100 bg-brand-50 px-4 py-3 text-sm text-brand-700">
          {notice}
        </p>
      )}
      <p className="rounded-lg border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
        {t.dashboard.demoNotice}
      </p>

      {!hasData ? (
        <EmptyState message={t.states.empty} />
      ) : (
        <>
          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4" aria-label={t.dashboard.title}>
            <KpiCard
              label={t.kpi.revenue}
              value={money(data.total_revenue)}
              change={data.comparison?.revenue_change_pct ?? null}
            />
            <KpiCard
              label={t.kpi.sales}
              value={String(data.total_sales)}
              change={data.comparison?.sales_change_pct ?? null}
            />
            <KpiCard
              label={t.kpi.avgTicket}
              value={money(data.avg_ticket)}
              change={data.comparison?.avg_ticket_change_pct ?? null}
            />
            <KpiCard
              label={t.kpi.topProduct}
              value={data.top_product?.name ?? t.kpi.noData}
              hint={data.top_product ? money(data.top_product.revenue) : null}
            />
          </section>

          <section className="grid gap-4 xl:grid-cols-2">
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm xl:col-span-2">
              <h3 className="mb-4 text-sm font-semibold text-slate-700">{t.charts.trend}</h3>
              {timeseries.data && timeseries.data.points.length > 0 ? (
                <SalesTrendChart points={timeseries.data.points} />
              ) : (
                <EmptyState />
              )}
            </article>
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-700">{t.charts.categories}</h3>
              {categories.data && categories.data.length > 0 ? (
                <CategoryBarChart data={categories.data} labelRevenue={t.charts.revenue} />
              ) : (
                <EmptyState />
              )}
            </article>
            <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
              <h3 className="mb-4 text-sm font-semibold text-slate-700">{t.charts.products}</h3>
              {products.data && products.data.length > 0 ? (
                <TopProductsChart data={products.data} labelRevenue={t.charts.revenue} />
              ) : (
                <EmptyState />
              )}
            </article>
          </section>
        </>
      )}
    </div>
  );
}
