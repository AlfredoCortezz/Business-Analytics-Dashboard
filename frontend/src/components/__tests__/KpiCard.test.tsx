import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { KpiCard } from "../KpiCard";
import { I18nProvider } from "../../i18n/I18nContext";

function renderWithI18n(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe("KpiCard", () => {
  it("muestra la etiqueta y el valor", () => {
    renderWithI18n(<KpiCard label="Ingresos" value="1.234,00" />);
    expect(screen.getByText("Ingresos")).toBeInTheDocument();
    expect(screen.getByText("1.234,00")).toBeInTheDocument();
  });

  it("muestra la variacion cuando se proporciona", () => {
    renderWithI18n(<KpiCard label="Ingresos" value="100" change={12.5} />);
    expect(screen.getByText(/12.5%/)).toBeInTheDocument();
  });

  it("muestra un hint cuando no hay variacion", () => {
    renderWithI18n(<KpiCard label="Producto" value="Café" hint="500" />);
    expect(screen.getByText("500")).toBeInTheDocument();
  });
});
