import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";
import { en } from "./en";
import { es, type Dictionary } from "./es";

export type Language = "es" | "en";

const dictionaries: Record<Language, Dictionary> = { es, en };
const STORAGE_KEY = "bad.language";

interface I18nContextValue {
  language: Language;
  setLanguage: (language: Language) => void;
  t: Dictionary;
}

const I18nContext = createContext<I18nContextValue | null>(null);

function detectLanguage(): Language {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored === "es" || stored === "en") return stored;
  return navigator.language.startsWith("en") ? "en" : "es";
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<Language>(() => detectLanguage());

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, language);
    document.documentElement.lang = language;
  }, [language]);

  const setLanguage = useCallback((next: Language) => setLanguageState(next), []);

  const value = useMemo<I18nContextValue>(
    () => ({ language, setLanguage, t: dictionaries[language] }),
    [language, setLanguage],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n(): I18nContextValue {
  const context = useContext(I18nContext);
  if (!context) throw new Error("useI18n debe usarse dentro de I18nProvider");
  return context;
}
