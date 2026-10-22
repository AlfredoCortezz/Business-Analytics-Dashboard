import { useEffect, useState } from "react";
import { useFilters } from "../context/FiltersContext";
import { useI18n } from "../i18n/I18nContext";
import { useDimensions } from "../hooks/useAsync";

export function FilterBar() {
  const { t } = useI18n();
  const { filters, setFilter, clear, hasActiveFilters } = useFilters();
  const { products, categories } = useDimensions();
  const [local, setLocal] = useState(filters);

  useEffect(() => setLocal(filters), [filters]);

  const inputClass =
    "w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:border-brand-500";

  return (
    <form
      className="flex flex-wrap items-end gap-3"
      onSubmit={(event) => {
        event.preventDefault();
        setFilter("date_from", local.date_from);
        setFilter("date_to", local.date_to);
        setFilter("product", local.product);
        setFilter("category", local.category);
      }}
      aria-label={t.filters.title}
    >
      <label htmlFor="filter-date-from" className="flex min-w-[9rem] flex-col gap-1 text-xs font-medium text-slate-600">
        {t.filters.dateFrom}
        <input
          id="filter-date-from"
          type="date"
          value={local.date_from}
          max={local.date_to || undefined}
          onChange={(event) => setLocal({ ...local, date_from: event.target.value })}
          className={inputClass}
        />
      </label>
      <label htmlFor="filter-date-to" className="flex min-w-[9rem] flex-col gap-1 text-xs font-medium text-slate-600">
        {t.filters.dateTo}
        <input
          id="filter-date-to"
          type="date"
          value={local.date_to}
          min={local.date_from || undefined}
          onChange={(event) => setLocal({ ...local, date_to: event.target.value })}
          className={inputClass}
        />
      </label>
      <label htmlFor="filter-product" className="flex min-w-[9rem] flex-col gap-1 text-xs font-medium text-slate-600">
        {t.filters.product}
        <select
          id="filter-product"
          value={local.product}
          onChange={(event) => setLocal({ ...local, product: event.target.value })}
          className={inputClass}
        >
          <option value="">{t.filters.all}</option>
          {products.map((product) => (
            <option key={product} value={product}>
              {product}
            </option>
          ))}
        </select>
      </label>
      <label htmlFor="filter-category" className="flex min-w-[9rem] flex-col gap-1 text-xs font-medium text-slate-600">
        {t.filters.category}
        <select
          id="filter-category"
          value={local.category}
          onChange={(event) => setLocal({ ...local, category: event.target.value })}
          className={inputClass}
        >
          <option value="">{t.filters.all}</option>
          {categories.map((category) => (
            <option key={category} value={category}>
              {category}
            </option>
          ))}
        </select>
      </label>
      <label htmlFor="filter-granularity" className="flex min-w-[8rem] flex-col gap-1 text-xs font-medium text-slate-600">
        {t.filters.granularity}
        <select
          id="filter-granularity"
          value={filters.granularity}
          onChange={(event) => setFilter("granularity", event.target.value)}
          className={inputClass}
        >
          <option value="day">{t.filters.day}</option>
          <option value="week">{t.filters.week}</option>
          <option value="month">{t.filters.month}</option>
        </select>
      </label>
      <label className="flex items-center gap-2 pb-2 text-sm text-slate-600">
        <input
          type="checkbox"
          checked={filters.compare}
          onChange={(event) => setFilter("compare", event.target.checked)}
          className="h-4 w-4 rounded border-slate-300 text-brand-600"
        />
        {t.filters.compare}
      </label>
      <div className="flex gap-2 pb-0.5">
        <button
          type="submit"
          className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700"
        >
          {t.filters.apply}
        </button>
        {hasActiveFilters && (
          <button
            type="button"
            onClick={clear}
            className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            {t.filters.clear}
          </button>
        )}
      </div>
    </form>
  );
}
