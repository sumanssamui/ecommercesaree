from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Table,
    TableStyle,
    Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
import os
from django.conf import settings


def generate_invoice_pdf(order):
    # ---------- Paths ----------
    invoice_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"invoice_{order.uid}.pdf")

    # ---------- Document ----------
    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
    )

    styles = getSampleStyleSheet()

    # ---------- Custom Styles ----------
    title_style = ParagraphStyle(
        "InvoiceTitle",
        parent=styles["Title"],
        fontSize=20,
        textColor=colors.HexColor("#222222"),
        spaceAfter=12,
    )

    label_style = ParagraphStyle(
        "Label",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.grey,
    )

    value_style = ParagraphStyle(
        "Value",
        parent=styles["Normal"],
        fontSize=11,
        leading=14,
    )

    elements = []

    # ---------- Header ----------
    elements.append(Paragraph("LOREAL INDIA", title_style))
    elements.append(Paragraph("<b>INVOICE</b>", styles["Heading2"]))
    elements.append(Spacer(1, 8))

    # ---------- Order Info ----------
    elements.append(Paragraph(f"<b>Order ID:</b> {order.uid}", value_style))
    elements.append(Paragraph(f"<b>Customer:</b> {order.user.full_name}", value_style))
    elements.append(Paragraph(f"<b>Email:</b> {order.user.email}", value_style))
    elements.append(Paragraph(f"<b>Status:</b> {order.status}", value_style))
    elements.append(Spacer(1, 14))

    # ---------- Table Data ----------
    data = [["Product", "Price (₹)", "Qty", "Total (₹)"]]

    for item in order.items.all():
        data.append([
            item.product.title,
            f"{item.price}",
            str(item.quantity),
            f"{item.total_price}",
        ])

    data.append(["", "", "Grand Total", f"{order.total_amount}"])

    # ---------- Table ----------
    table = Table(data, colWidths=[230, 80, 50, 90])

    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),

        # Body
        ("FONTNAME", (0, 1), (-1, -2), "Helvetica"),
        ("FONTSIZE", (0, 1), (-1, -2), 9),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),

        # Total row
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e5e7eb")),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),

        # Grid
        ("GRID", (0, 0), (-1, -1), 0.7, colors.grey),

        # Padding
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 16))

    # ---------- Footer ----------
    elements.append(
        Paragraph(
            "Thank you for shopping with Loreal India.",
            ParagraphStyle(
                "Footer",
                parent=styles["Normal"],
                fontSize=9,
                textColor=colors.grey,
                alignment=1,  # center
            ),
        )
    )

    # ---------- Build ----------
    doc.build(elements)

    return file_path
