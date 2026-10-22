import type {
  CategoryPoint,
  DemoResponse,
  Dimensions,
  ImportRecord,
  Paginated,
  ProductPoint,
  Sale,
  Summary,
  Timeseries,
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    let detail = `Error ${response.status}`;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") detail = payload.detail;
    } catch {
      /* respuesta sin cuerpo JSON */
    }
    throw new ApiError(detail, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

function toQuery(params: Record<string, string | number | boolean | undefined | null>): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "" || value === false) return;
    search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `?${query}` : "";
}

export type AnalyticsParams = Record<string, string | number | boolean | undefined | null>;

export const api = {
  health: () => request<{ status: string; version: string; database: string }>("/health"),

  listImports: (page = 1, pageSize = 20) =>
    request<Paginated<ImportRecord>>(`/imports${toQuery({ page, page_size: pageSize })}`),

  getImport: (id: number) => request<ImportRecord>(`/imports/${id}`),

  uploadImport: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<ImportRecord>("/imports", { method: "POST", body: form });
  },

  confirmImport: (id: number) => request<ImportRecord>(`/imports/${id}/confirm`, { method: "POST" }),

  deleteImport: (id: number) => request<void>(`/imports/${id}`, { method: "DELETE" }),

  listSales: (params: AnalyticsParams, page = 1, pageSize = 20, sortBy = "fecha", sortOrder = "desc") =>
    request<Paginated<Sale>>(
      `/sales${toQuery({ ...params, page, page_size: pageSize, sort_by: sortBy, sort_order: sortOrder })}`,
    ),

  getSale: (id: number) => request<Sale>(`/sales/${id}`),

  summary: (params: AnalyticsParams) => request<Summary>(`/analytics/summary${toQuery(params)}`),

  timeseries: (params: AnalyticsParams) => request<Timeseries>(`/analytics/timeseries${toQuery(params)}`),

  categories: (params: AnalyticsParams) => request<CategoryPoint[]>(`/analytics/categories${toQuery(params)}`),

  products: (params: AnalyticsParams, limit = 10) =>
    request<ProductPoint[]>(`/analytics/products${toQuery({ ...params, limit })}`),

  dimensions: () => request<Dimensions>("/analytics/dimensions"),

  seedDemo: () => request<DemoResponse>("/demo/seed", { method: "POST" }),

  resetDemo: () => request<DemoResponse>("/demo/seed", { method: "DELETE" }),

  reportCsvUrl: (params: AnalyticsParams) => `${API_BASE}/reports/csv${toQuery(params)}`,

  reportPdfUrl: (params: AnalyticsParams) => `${API_BASE}/reports/pdf${toQuery(params)}`,
};
