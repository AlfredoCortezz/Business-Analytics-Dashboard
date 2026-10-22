import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import { FilterBar } from "../FilterBar";
import { FiltersProvider } from "../../context/FiltersContext";
import { I18nProvider } from "../../i18n/I18nContext";

function renderFilterBar() {
  return render(
    <I18nProvider>
      <MemoryRouter>
        <FiltersProvider>
          <FilterBar />
        </FiltersProvider>
      </MemoryRouter>
    </I18nProvider>,
  );
}

describe("FilterBar", () => {
  it("renderiza los controles de filtro", () => {
    renderFilterBar();
    expect(screen.getByLabelText(/Desde/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Hasta/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Producto/)).toBeInTheDocument();
    expect(screen.getByLabelText(/Categoría/)).toBeInTheDocument();
  });

  it("permite escribir una fecha", () => {
    renderFilterBar();
    const input = screen.getByLabelText(/Desde/);
    fireEvent.change(input, { target: { value: "2024-01-01" } });
    expect(input).toHaveValue("2024-01-01");
  });
});
