import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmptyState, ErrorState, LoadingState } from "../states/States";
import { I18nProvider } from "../../i18n/I18nContext";

function renderWithI18n(ui: React.ReactElement) {
  return render(<I18nProvider>{ui}</I18nProvider>);
}

describe("Estados de la interfaz", () => {
  it("LoadingState anuncia el estado de carga", () => {
    renderWithI18n(<LoadingState />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("ErrorState muestra el mensaje y el boton de reintento", () => {
    renderWithI18n(<ErrorState message="Fallo de red" onRetry={() => undefined} />);
    expect(screen.getByRole("alert")).toBeInTheDocument();
    expect(screen.getByText("Fallo de red")).toBeInTheDocument();
    expect(screen.getByRole("button")).toBeInTheDocument();
  });

  it("EmptyState muestra el texto por defecto", () => {
    renderWithI18n(<EmptyState />);
    expect(screen.getByRole("status")).toBeInTheDocument();
  });
});
