import { useState, type ReactNode } from "react";
import { useI18n } from "../i18n/I18nContext";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";

export function Layout({ children, toolbar }: { children: ReactNode; toolbar?: ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { t } = useI18n();

  return (
    <div className="flex min-h-screen bg-slate-100">
      <a href="#main" className="skip-link">
        {t.nav.dashboard}
      </a>
      {sidebarOpen && (
        <button
          type="button"
          aria-label="Cerrar navegación"
          className="fixed inset-0 z-20 bg-slate-900/40 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <Sidebar open={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header onToggleSidebar={() => setSidebarOpen((value) => !value)} />
        {toolbar && <div className="border-b border-slate-200 bg-white px-4 py-3 lg:px-6">{toolbar}</div>}
        <main id="main" className="flex-1 p-4 lg:p-6">
          {children}
        </main>
      </div>
    </div>
  );
}
