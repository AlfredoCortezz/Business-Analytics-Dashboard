import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { CategoryPoint, ProductPoint, TimeseriesPoint } from "../../types";

const PALETTE = ["#2563eb", "#7c3aed", "#059669", "#d97706", "#dc2626", "#0891b2", "#db2777", "#65a30d"];

const currency = (value: number) =>
  new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);

export function SalesTrendChart({ points }: { points: TimeseriesPoint[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={points} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="period" tick={{ fontSize: 11 }} angle={-30} textAnchor="end" height={50} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={currency} />
        <Tooltip formatter={(value: number) => currency(value)} />
        <Line type="monotone" dataKey="revenue" stroke="#2563eb" strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function CategoryBarChart({ data, labelRevenue }: { data: CategoryPoint[]; labelRevenue: string }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="category" tick={{ fontSize: 11 }} angle={-20} textAnchor="end" height={50} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={currency} />
        <Tooltip formatter={(value: number) => currency(value)} />
        <Bar dataKey="revenue" name={labelRevenue} fill="#7c3aed" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function TopProductsChart({ data, labelRevenue }: { data: ProductPoint[]; labelRevenue: string }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          dataKey="revenue"
          nameKey="product"
          name={labelRevenue}
          innerRadius={55}
          outerRadius={95}
          paddingAngle={2}
        >
          {data.map((entry, index) => (
            <Cell key={entry.product} fill={PALETTE[index % PALETTE.length]} />
          ))}
        </Pie>
        <Legend wrapperStyle={{ fontSize: 11 }} />
        <Tooltip formatter={(value: number) => currency(value)} />
      </PieChart>
    </ResponsiveContainer>
  );
}
