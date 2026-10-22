import { createContext, useCallback, useContext, useMemo } from "react";
import type { ReactNode } from "react";
import { useSearchParams } from "react-router-dom";
import type { ActiveFilters } from "../types";

interface FiltersContextValue {
  filters: ActiveFilters;
  query: AnalyticsParams;
  setFilter: (key: keyof ActiveFilters, value: string | boolean) => void;
  setFilters: (values: Partial<ActiveFilters>) => void;
  clear: () => void;
  hasActiveFilters: boolean;
}

type AnalyticsParams = Record<string, string | boolean>;

const FilterContext = createContext<FiltersContextValue | null>(null);

const defaultFilters: ActiveFilters = {
  date_from: "",
  date_to: "",
  product: "",
  category: "",
  compare: false,
  granularity: "day",
};

export function FiltersProvider({ children }: { children: ReactNode }) {
  const [searchParams, setSearchParams] = useSearchParams();

  const filters = useMemo<ActiveFilters>(
    () => ({
      date_from: searchParams.get("date_from") ?? defaultFilters.date_from,
      date_to: searchParams.get("date_to") ?? defaultFilters.date_to,
      product: searchParams.get("product") ?? defaultFilters.product,
      category: searchParams.get("category") ?? defaultFilters.category,
      compare: searchParams.get("compare") === "true",
      granularity:
        (searchParams.get("granularity") as ActiveFilters["granularity"]) ??
        defaultFilters.granularity,
    }),
    [searchParams],
  );

  const setFilter = useCallback(
    (key: keyof ActiveFilters, value: string | boolean) => {
      const next = new URLSearchParams(searchParams);
      const isEmpty = value === "" || value === false || value === defaultFilters[key];
      if (isEmpty) next.delete(key);
      else next.set(key, String(value));
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const setFilters = useCallback(
    (values: Partial<ActiveFilters>) => {
      const next = new URLSearchParams(searchParams);
      Object.entries(values).forEach(([key, value]) => {
        const isEmpty = value === "" || value === false || value === defaultFilters[key as keyof ActiveFilters];
        if (isEmpty) next.delete(key);
        else next.set(key, String(value));
      });
      setSearchParams(next, { replace: true });
    },
    [searchParams, setSearchParams],
  );

  const clear = useCallback(() => setSearchParams(new URLSearchParams(), { replace: true }), [setSearchParams]);

  const query = useMemo<AnalyticsParams>(() => {
    const params: AnalyticsParams = {};
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    if (filters.product) params.product = filters.product;
    if (filters.category) params.category = filters.category;
    if (filters.compare) params.compare = true;
    if (filters.granularity) params.granularity = filters.granularity;
    return params;
  }, [filters]);

  const hasActiveFilters = Boolean(
    filters.date_from || filters.date_to || filters.product || filters.category,
  );

  const value = useMemo<FiltersContextValue>(
    () => ({ filters, query, setFilter, setFilters, clear, hasActiveFilters }),
    [filters, query, setFilter, setFilters, clear, hasActiveFilters],
  );

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}

export function useFilters(): FiltersContextValue {
  const context = useContext(FilterContext);
  if (!context) throw new Error("useFilters debe usarse dentro de FiltersProvider");
  return context;
}
