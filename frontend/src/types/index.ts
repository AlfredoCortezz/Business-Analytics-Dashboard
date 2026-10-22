export interface ImportErrorItem {
  row: number;
  field: string | null;
  message: string;
}

export interface ImportRecord {
  id: number;
  filename: string;
  status: "pending" | "confirmed" | "failed" | "discarded";
  total_rows: number;
  accepted_rows: number;
  rejected_rows: number;
  duplicate_rows: number;
  is_demo: boolean;
  created_at: string;
  confirmed_at: string | null;
  errors?: ImportErrorItem[];
}

export interface Sale {
  id: number;
  import_id: number;
  fecha: string;
  producto: string;
  categoria: string;
  cantidad: number;
  precio_unitario: string;
  total: string;
  row_warnings: string[];
}

export interface Paginated<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface Period {
  date_from: string | null;
  date_to: string | null;
}

export interface TopProduct {
  name: string;
  revenue: number;
  quantity: number;
}

export interface Comparison {
  previous_revenue: number;
  previous_sales: number;
  previous_avg_ticket: number;
  revenue_change_pct: number | null;
  sales_change_pct: number | null;
  avg_ticket_change_pct: number | null;
  previous_period: Period;
}

export interface Summary {
  total_revenue: number;
  total_sales: number;
  avg_ticket: number;
  top_product: TopProduct | null;
  period: Period;
  comparison: Comparison | null;
}

export interface TimeseriesPoint {
  period: string;
  revenue: number;
  sales_count: number;
}

export interface Timeseries {
  granularity: "day" | "week" | "month";
  points: TimeseriesPoint[];
}

export interface CategoryPoint {
  category: string;
  revenue: number;
  sales_count: number;
  percentage: number;
}

export interface ProductPoint {
  product: string;
  revenue: number;
  quantity: number;
  sales_count: number;
}

export interface Dimensions {
  products: string[];
  categories: string[];
}

export interface DemoResponse {
  created: boolean;
  imports: number;
  sales: number;
  message: string;
}

export interface ActiveFilters {
  date_from: string;
  date_to: string;
  product: string;
  category: string;
  compare: boolean;
  granularity: "day" | "week" | "month";
}
