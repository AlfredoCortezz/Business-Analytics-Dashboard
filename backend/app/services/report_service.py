import csv
import io
from datetime import datetime, timezone
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.shapes import Drawing, String
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.models import Sale
from app.services import analytics_service

PRIMARY = colors.HexColor("#2563eb")
ACCENT = colors.HexColor("#7c3aed")
GRID = colors.HexColor("#cbd5e1")


def build_csv(sales: list[Sale]) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["id", "fecha", "producto", "categoria", "cantidad", "precio_unitario", "total", "import_id"]
    )
    for sale in sales:
        writer.writerow(
            [
                sale.id,
                sale.fecha.isoformat(),
                sale.producto,
                sale.categoria,
                sale.cantidad,
                f"{sale.precio_unitario:.2f}",
                f"{sale.total:.2f}",
                sale.import_id,
            ]
        )
    return buffer.getvalue()


def _line_chart(points: list) -> Drawing:
    drawing = Drawing(460, 200)
    chart = HorizontalLineChart()
    chart.x = 40
    chart.y = 30
    chart.height = 130
    chart.width = 400
    chart.data = [[point.revenue for point in points]]
    chart.lines[0].strokeColor = PRIMARY
    chart.lines[0].strokeWidth = 2
    chart.categoryAxis.categoryNames = [point.period for point in points]
    chart.categoryAxis.labels.fontSize = 6
    chart.categoryAxis.labels.angle = 45
    chart.categoryAxis.labels.dy = -8
    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontSize = 7
    drawing.add(chart)
    return drawing


def _bar_chart(categories: list) -> Drawing:
    drawing = Drawing(460, 210)
    chart = VerticalBarChart()
    chart.x = 40
    chart.y = 30
    chart.height = 130
    chart.width = 400
    chart.data = [[item.revenue for item in categories[:8]]]
    chart.bars[0].fillColor = ACCENT
    chart.categoryAxis.categoryNames = [item.category for item in categories[:8]]
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.angle = 30
    chart.categoryAxis.labels.dy = -10
    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontSize = 7
    drawing.add(chart)
    return drawing


def _pie_chart(products: list) -> Drawing:
    drawing = Drawing(460, 220)
    pie = Pie()
    pie.x = 40
    pie.y = 20
    pie.width = 160
    pie.height = 160
    pie.data = [item.revenue for item in products[:6]] or [1]
    pie.labels = [f"{item.product}" for item in products[:6]] or [""]
    pie.slices.strokeWidth = 0.5
    drawing.add(pie)

    legend = Legend()
    legend.x = 230
    legend.y = 160
    legend.fontSize = 7
    legend.alignment = "right"
    palette = [colors.HexColor("#2563eb"), colors.HexColor("#7c3aed"), colors.HexColor("#059669"),
               colors.HexColor("#d97706"), colors.HexColor("#dc2626"), colors.HexColor("#0891b2")]
    for index, _ in enumerate(products[:6]):
        pie.slices[index].fillColor = palette[index % len(palette)]
        legend.colorNamePairs.append((palette[index % len(palette)], products[index].product))
    drawing.add(legend)
    return drawing


def build_pdf(db, *, filters: dict, period: dict, summary) -> bytes:
    buffer = io.BytesIO()
    document = SimpleDocTemplate(buffer, pagesize=A4, title="Reporte Business Analytics")
    styles = getSampleStyleSheet()
    story: list = []

    story.append(Paragraph("Reporte de Business Analytics", styles["Title"]))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    story.append(Paragraph(f"Fecha de generación: {generated}", styles["Normal"]))
    period_text = f"Periodo analizado: {period.get('date_from') or 'inicio'} a {period.get('date_to') or 'hoy'}"
    story.append(Paragraph(period_text, styles["Normal"]))
    active = ", ".join(f"{key}={escape(str(value))}" for key, value in filters.items() if value)
    story.append(Paragraph(f"Filtros activos: {active or 'ninguno'}", styles["Normal"]))
    story.append(Spacer(1, 0.4 * cm))

    kpi_data = [
        ["Indicador", "Valor"],
        ["Ingresos totales", f"{summary.total_revenue:,.2f}"],
        ["Número de ventas", f"{summary.total_sales:,}"],
        ["Ticket promedio", f"{summary.avg_ticket:,.2f}"],
        ["Producto más vendido", summary.top_product.name if summary.top_product else "Sin datos"],
    ]
    if summary.comparison:
        kpi_data.append(["Variación de ingresos", f"{summary.comparison.revenue_change_pct}%"])
    kpi_table = Table(kpi_data, colWidths=[7 * cm, 8 * cm])
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ]
        )
    )
    story.append(kpi_table)
    story.append(Spacer(1, 0.5 * cm))

    timeseries = analytics_service.build_timeseries(db, **filters)
    if timeseries.points:
        story.append(Paragraph("Evolución de ventas", styles["Heading2"]))
        story.append(_line_chart(timeseries.points))
        story.append(Spacer(1, 0.4 * cm))

    categories = analytics_service.build_categories(db, **filters)
    if categories:
        story.append(Paragraph("Distribución de ingresos por categoría", styles["Heading2"]))
        story.append(_bar_chart(categories))
        story.append(Spacer(1, 0.4 * cm))

    products = analytics_service.build_products(db, limit=10, **filters)
    if products:
        story.append(Paragraph("Productos más vendidos", styles["Heading2"]))
        story.append(_pie_chart(products))
        rows = [["Producto", "Ingresos", "Cantidad"]] + [
            [item.product, f"{item.revenue:,.2f}", str(item.quantity)] for item in products[:10]
        ]
        table = Table(rows, colWidths=[8 * cm, 4 * cm, 3 * cm])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("GRID", (0, 0), (-1, -1), 0.4, GRID),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(table)

    document.build(story)
    return buffer.getvalue()
