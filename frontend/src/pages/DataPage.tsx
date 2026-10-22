import { useState } from "react";
import { api } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/states/States";
import { useFilters } from "../context/FiltersContext";
import { useAsync } from "../hooks/useAsync";
import { useI18n } from "../i18n/I18nContext";
import type { Sale } from "../types";

const money = (value: string | number) =>
  new Intl.NumberFormat(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value));

export function DataPage() {
  const { t } = useI18n();
  const { filters, query } = useFilters();
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState("fecha");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [selected, setSelected] = useState<Sale | null>(null);

  const key = JSON.stringify({ filters, page, sortBy, sortOrder });
  const sales = useAsync(() => api.listSales(query, page, 20, sortBy, sortOrder), [key]);

  const totalPages = sales.data ? Math.max(1, Math.ceil(sales.data.total / sales.data.page_size)) : 1;

  const toggleSort = (column: string) => {
    if (sortBy === column) setSortOrder((order) => (order === "asc" ? "desc" : "asc"));
    else {
      setSortBy(column);
      setSortOrder("asc");
    }
  };

  const columns: Array<[string, string]> = [
    ["fecha", t.data.date],
    ["producto", t.data.product],
    ["categoria", t.data.category],
    ["cantidad", t.data.quantity],
    ["precio_unitario", t.data.unitPrice],
    ["total", t.data.total],
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h2 className="text-xl font-semibold text-slate-900">{t.data.title}</h2>
          <p className="mt-1 text-sm text-slate-500">{t.data.subtitle}</p>
        </div>
        {sales.data && (
          <p className="text-sm text-slate-500">
            {t.data.results.replace("{count}", String(sales.data.total))}
          </p>
        )}
      </div>

      {sales.loading ? (
        <LoadingState />
      ) : sales.error ? (
        <ErrorState message={sales.error} onRetry={sales.reload} />
      ) : !sales.data || sales.data.items.length === 0 ? (
        <EmptyState message={t.data.noResults} />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                {columns.map(([column, label]) => (
                  <th key={column} scope="col" className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => toggleSort(column)}
                      className="flex items-center gap-1 font-semibold uppercase hover:text-slate-800"
                    >
                      {label}
                      {sortBy === column && <span aria-hidden="true">{sortOrder === "asc" ? "▲" : "▼"}</span>}
                    </button>
                  </th>
                ))}
                <th scope="col" className="px-3 py-2">
                  {t.data.origin}
                </th>
                <th scope="col" className="px-3 py-2" />
              </tr>
            </thead>
            <tbody>
              {sales.data.items.map((sale) => (
                <tr key={sale.id} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="px-3 py-2">{sale.fecha}</td>
                  <td className="px-3 py-2">{sale.producto}</td>
                  <td className="px-3 py-2">{sale.categoria}</td>
                  <td className="px-3 py-2">{sale.cantidad}</td>
                  <td className="px-3 py-2">{money(sale.precio_unitario)}</td>
                  <td className="px-3 py-2 font-medium">{money(sale.total)}</td>
                  <td className="px-3 py-2 text-slate-500">#{sale.import_id}</td>
                  <td className="px-3 py-2">
                    <button
                      type="button"
                      onClick={() => setSelected(sale)}
                      className="text-brand-600 hover:underline"
                    >
                      {t.data.detail}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-between">
        <button
          type="button"
          disabled={page <= 1}
          onClick={() => setPage((value) => Math.max(1, value - 1))}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
        >
          {t.data.prev}
        </button>
        <span className="text-sm text-slate-500">
          {t.data.page.replace("{page}", String(page)).replace("{pages}", String(totalPages))}
        </span>
        <button
          type="button"
          disabled={page >= totalPages}
          onClick={() => setPage((value) => value + 1)}
          className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100 disabled:opacity-50"
        >
          {t.data.next}
        </button>
      </div>

      {selected && (
        <div
          role="dialog"
          aria-modal="true"
          aria-label={t.data.detail}
          className="fixed inset-0 z-40 flex items-center justify-center bg-slate-900/40 p-4"
          onClick={() => setSelected(null)}
        >
          <div
            className="w-full max-w-md rounded-xl bg-white p-5 shadow-xl"
            onClick={(event) => event.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <h3 className="text-base font-semibold text-slate-900">{t.data.detail}</h3>
              <button
                type="button"
                onClick={() => setSelected(null)}
                className="text-slate-400 hover:text-slate-600"
              >
                ✕
              </button>
            </div>
            <dl className="mt-4 space-y-2 text-sm">
              {[
                [t.data.date, selected.fecha],
                [t.data.product, selected.producto],
                [t.data.category, selected.categoria],
                [t.data.quantity, String(selected.cantidad)],
                [t.data.unitPrice, money(selected.precio_unitario)],
                [t.data.total, money(selected.total)],
                [t.data.origin, `#${selected.import_id}`],
              ].map(([label, value]) => (
                <div key={label} className="flex justify-between border-b border-slate-100 pb-1">
                  <dt className="text-slate-500">{label}</dt>
                  <dd className="font-medium text-slate-800">{value}</dd>
                </div>
              ))}
            </dl>
            {selected.row_warnings.length > 0 && (
              <div className="mt-4 rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
                <p className="font-medium">{t.data.warnings}</p>
                <ul className="mt-1 list-disc pl-5">
                  {selected.row_warnings.map((warning) => (
                    <li key={warning}>{warning}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
