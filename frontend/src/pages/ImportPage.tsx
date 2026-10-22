import { useRef, useState } from "react";
import { api, ApiError } from "../api/client";
import { EmptyState, ErrorState, LoadingState } from "../components/states/States";
import { useAsync } from "../hooks/useAsync";
import { useI18n } from "../i18n/I18nContext";
import type { Dictionary } from "../i18n/es";
import type { ImportRecord } from "../types";

export function ImportPage() {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);
  const [selected, setSelected] = useState<ImportRecord | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState<string | null>(null);

  const history = useAsync(() => api.listImports(), []);

  const handleFile = async (file: File) => {
    setUploading(true);
    setError(null);
    setNotice(null);
    try {
      const record = await api.uploadImport(file);
      const detail = await api.getImport(record.id);
      setSelected(detail);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : (err as Error).message);
    } finally {
      setUploading(false);
    }
  };

  const confirmImport = async () => {
    if (!selected) return;
    try {
      await api.confirmImport(selected.id);
      setSelected(null);
      setNotice(t.import.confirmed);
      history.reload();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const discardImport = async () => {
    if (!selected) return;
    try {
      await api.deleteImport(selected.id);
      setSelected(null);
      history.reload();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  const deleteImport = async (id: number) => {
    if (!window.confirm(t.import.deleteConfirm)) return;
    await api.deleteImport(id);
    history.reload();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-semibold text-slate-900">{t.import.title}</h2>
        <p className="mt-1 text-sm text-slate-500">{t.import.subtitle}</p>
      </div>

      {notice && (
        <p role="status" className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          {notice}
        </p>
      )}

      <div
        className="rounded-xl border-2 border-dashed border-slate-300 bg-white p-8 text-center"
        onDragOver={(event) => event.preventDefault()}
        onDrop={(event) => {
          event.preventDefault();
          const file = event.dataTransfer.files?.[0];
          if (file) void handleFile(file);
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv,.xlsx"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) void handleFile(file);
            event.target.value = "";
          }}
        />
        <p className="text-slate-600">{t.import.dropzone}</p>
        <p className="mt-1 text-xs text-slate-400">{t.import.supported.replace("{size}", "5")}</p>
        <button
          type="button"
          disabled={uploading}
          onClick={() => inputRef.current?.click()}
          className="mt-4 rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
        >
          {uploading ? t.import.analyzing : t.import.upload}
        </button>
      </div>

      {error && <ErrorState message={error} />}

      {selected && (
        <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700">{t.import.review}</h3>
          <dl className="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
            {[
              [t.import.totalRows, selected.total_rows],
              [t.import.accepted, selected.accepted_rows],
              [t.import.rejected, selected.rejected_rows],
              [t.import.duplicates, selected.duplicate_rows],
            ].map(([label, value]) => (
              <div key={String(label)} className="rounded-lg bg-slate-50 p-3">
                <dt className="text-xs text-slate-500">{label}</dt>
                <dd className="text-lg font-semibold text-slate-900">{value}</dd>
              </div>
            ))}
          </dl>

          <div className="mt-4">
            <h4 className="text-sm font-medium text-slate-600">{t.import.errors}</h4>
            {selected.errors && selected.errors.length > 0 ? (
              <div className="mt-2 max-h-60 overflow-auto rounded-lg border border-slate-200">
                <table className="w-full text-left text-sm">
                  <thead className="bg-slate-50 text-xs uppercase text-slate-500">
                    <tr>
                      <th className="px-3 py-2">{t.import.row}</th>
                      <th className="px-3 py-2">{t.import.field}</th>
                      <th className="px-3 py-2">{t.import.message}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selected.errors.map((item, index) => (
                      <tr key={`${item.row}-${index}`} className="border-t border-slate-100">
                        <td className="px-3 py-2">{item.row}</td>
                        <td className="px-3 py-2">{item.field ?? "—"}</td>
                        <td className="px-3 py-2">{item.message}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-2 text-sm text-slate-500">{t.import.noErrors}</p>
            )}
          </div>

          <div className="mt-4 flex gap-2">
            <button
              type="button"
              onClick={confirmImport}
              disabled={selected.accepted_rows === 0}
              className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-50"
            >
              {t.import.confirm}
            </button>
            <button
              type="button"
              onClick={discardImport}
              className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
            >
              {t.import.discard}
            </button>
          </div>
        </section>
      )}

      <section className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700">{t.import.history}</h3>
        {history.loading ? (
          <LoadingState />
        ) : history.error ? (
          <ErrorState message={history.error} onRetry={history.reload} />
        ) : !history.data || history.data.items.length === 0 ? (
          <div className="mt-3">
            <EmptyState message={t.import.noImports} />
          </div>
        ) : (
          <div className="mt-3 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-slate-200 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-3 py-2">{t.import.filename}</th>
                  <th className="px-3 py-2">{t.import.status}</th>
                  <th className="px-3 py-2">{t.import.accepted}</th>
                  <th className="px-3 py-2">{t.import.rejected}</th>
                  <th className="px-3 py-2">{t.import.duplicates}</th>
                  <th className="px-3 py-2">{t.import.createdAt}</th>
                  <th className="px-3 py-2">{t.import.actions}</th>
                </tr>
              </thead>
              <tbody>
                {history.data.items.map((record) => (
                  <tr key={record.id} className="border-b border-slate-100">
                    <td className="px-3 py-2">
                      {record.filename}
                      {record.is_demo && (
                        <span className="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-xs font-medium text-amber-700">
                          {t.import.demoTag}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2">{statusLabel(record.status, t)}</td>
                    <td className="px-3 py-2">{record.accepted_rows}</td>
                    <td className="px-3 py-2">{record.rejected_rows}</td>
                    <td className="px-3 py-2">{record.duplicate_rows}</td>
                    <td className="px-3 py-2">{new Date(record.created_at).toLocaleString()}</td>
                    <td className="px-3 py-2">
                      {record.status === "pending" && (
                        <button
                          type="button"
                          onClick={async () => {
                            const detail = await api.getImport(record.id);
                            setSelected(detail);
                            window.scrollTo({ top: 0, behavior: "smooth" });
                          }}
                          className="text-brand-600 hover:underline"
                        >
                          {t.import.review}
                        </button>
                      )}
                      <button
                        type="button"
                        onClick={() => deleteImport(record.id)}
                        className="ml-3 text-red-600 hover:underline"
                      >
                        {t.import.delete}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

function statusLabel(status: ImportRecord["status"], t: Dictionary): string {
  const map: Record<string, string> = {
    pending: t.import.statusPending,
    confirmed: t.import.statusConfirmed,
    failed: t.import.statusFailed,
    discarded: t.import.statusDiscarded,
  };
  return map[status] ?? status;
}
