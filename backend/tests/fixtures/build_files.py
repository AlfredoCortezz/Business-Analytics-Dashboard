import io
from datetime import date, timedelta

import pandas as pd


def sales_dataframe() -> pd.DataFrame:
    base = date(2024, 1, 1)
    rows = []
    for index in range(10):
        rows.append(
            {
                "fecha": (base + timedelta(days=index)).isoformat(),
                "producto": ["Café", "Té", "Café", "Jugo", "Té", "Café", "Jugo", "Té", "Café", "Jugo"][index],
                "categoria": ["Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas", "Bebidas"][index],
                "cantidad": [2, 1, 3, 4, 2, 5, 1, 3, 2, 6][index],
                "precio_unitario": [8.5, 6.0, 8.5, 4.2, 6.0, 8.5, 4.2, 6.0, 8.5, 4.2][index],
                "ventas_totales": [17.0, 6.0, 25.5, 16.8, 12.0, 42.5, 4.2, 18.0, 17.0, 25.2][index],
            }
        )
    return pd.DataFrame(rows)


def csv_bytes(dataframe: pd.DataFrame | None = None) -> bytes:
    frame = dataframe if dataframe is not None else sales_dataframe()
    return frame.to_csv(index=False).encode("utf-8")


def xlsx_bytes(dataframe: pd.DataFrame | None = None) -> bytes:
    frame = dataframe if dataframe is not None else sales_dataframe()
    buffer = io.BytesIO()
    frame.to_excel(buffer, index=False, engine="openpyxl")
    return buffer.getvalue()


def csv_with_bad_rows() -> bytes:
    content = (
        "fecha,producto,categoria,cantidad,precio_unitario,ventas_totales\n"
        "2024-02-01,Café,Bebidas,2,8.50,17.00\n"
        "fecha-invalida,Té,Bebidas,1,6.00,6.00\n"
        "2024-02-03,,Bebidas,3,8.50,25.50\n"
        "2024-02-04,Jugo,Bebidas,abc,4.20,16.80\n"
        "2024-02-05,Té,Bebidas,-2,6.00,12.00\n"
        "2024-02-07,Jugo,Bebidas,1,precio,4.20\n"
        "2024-02-06,Café,Bebidas,2,8.50,17.00\n"
        "2024-02-06,Café,Bebidas,2,8.50,17.00\n"
    )
    return content.encode("utf-8")


def csv_missing_columns() -> bytes:
    content = "fecha,producto\n2024-01-01,Café\n"
    return content.encode("utf-8")
