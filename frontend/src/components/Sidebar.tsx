import { NavLink } from "react-router-dom";
import { useI18n } from "../i18n/I18nContext";

const navItems = [
  { to: "/", key: "dashboard", icon: "▤" },
  { to: "/import", key: "import", icon: "⬆" },
  { to: "/data", key: "data", icon: "☰" },
  { to: "/reports", key: "reports", icon: "⎙" },
] as const;

export function Sidebar({ open, onNavigate }: { open: boolean; onNavigate: () => void }) {
  const { t } = useI18n();
  return (
    <aside
      aria-label={t.app.name}
      className={`fixed inset-y-0 left-0 z-30 w-64 transform border-r border-slate-200 bg-white transition-transform lg:static lg:translate-x-0 ${
        open ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      <div className="flex h-16 items-center gap-2 border-b border-slate-200 px-5">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-brand-600 text-lg font-bold text-white">
          B
        </span>
        <span className="text-sm font-semibold uppercase tracking-wide text-slate-700">Analytics</span>
      </div>
      <nav className="p-3">
        <ul className="space-y-1">
          {navItems.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                end={item.to === "/"}
                onClick={onNavigate}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-brand-50 text-brand-700"
                      : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                  }`
                }
              >
                <span aria-hidden="true">{item.icon}</span>
                {t.nav[item.key]}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}
