import { useI18n } from "../i18n/I18nContext";

export function Header({ onToggleSidebar }: { onToggleSidebar: () => void }) {
  const { t, language, setLanguage } = useI18n();
  return (
    <header className="flex h-16 items-center justify-between gap-4 border-b border-slate-200 bg-white px-4 lg:px-6">
      <button
        type="button"
        onClick={onToggleSidebar}
        className="rounded-lg border border-slate-200 p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
        aria-label="Abrir navegación"
      >
        ☰
      </button>
      <div className="min-w-0">
        <h1 className="truncate text-base font-semibold text-slate-900">{t.app.name}</h1>
        <p className="hidden truncate text-xs text-slate-500 sm:block">{t.app.tagline}</p>
      </div>
      <label className="flex items-center gap-2 text-sm text-slate-600">
        <span className="sr-only">Idioma / Language</span>
        <select
          value={language}
          onChange={(event) => setLanguage(event.target.value as "es" | "en")}
          className="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-sm focus:border-brand-500"
          aria-label="Idioma / Language"
        >
          <option value="es">Español</option>
          <option value="en">English</option>
        </select>
      </label>
    </header>
  );
}
