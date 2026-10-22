import { useI18n } from "../../i18n/I18nContext";

export function LoadingState({ label }: { label?: string }) {
  const { t } = useI18n();
  return (
    <div role="status" aria-live="polite" className="flex items-center justify-center gap-3 py-10 text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-600" />
      <span>{label ?? t.states.loading}</span>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message?: string; onRetry?: () => void }) {
  const { t } = useI18n();
  return (
    <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
      <p className="font-medium">{t.states.error}</p>
      {message && <p className="mt-1 text-sm">{message}</p>}
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          className="mt-3 rounded bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
        >
          {t.states.retry}
        </button>
      )}
    </div>
  );
}

export function EmptyState({ message }: { message?: string }) {
  const { t } = useI18n();
  return (
    <div role="status" className="rounded-lg border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-slate-500">
      {message ?? t.states.empty}
    </div>
  );
}
