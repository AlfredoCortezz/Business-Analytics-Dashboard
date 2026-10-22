import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { FilterBar } from "./components/FilterBar";
import { FiltersProvider } from "./context/FiltersContext";
import { DashboardPage } from "./pages/DashboardPage";
import { DataPage } from "./pages/DataPage";
import { ImportPage } from "./pages/ImportPage";
import { ReportsPage } from "./pages/ReportsPage";

export default function App() {
  return (
    <FiltersProvider>
      <Layout toolbar={<FilterBar />}>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/import" element={<ImportPage />} />
          <Route path="/data" element={<DataPage />} />
          <Route path="/reports" element={<ReportsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </FiltersProvider>
  );
}
