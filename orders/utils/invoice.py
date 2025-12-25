from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from django.conf import settings


def generate_invoice_pdf(order):
    invoice_dir = os.path.join(settings.MEDIA_ROOT, "invoices")
    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"invoice_{order.uid}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Saree Store - Invoice</b>", styles["Title"]))
    elements.append(Paragraph(f"Order ID: {order.uid}", styles["Normal"]))
    elements.append(Paragraph(f"Customer: {order.user.full_name}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {order.user.email}", styles["Normal"]))
    elements.append(Paragraph(f"Status: {order.status}", styles["Normal"]))
    elements.append(Paragraph("<br/>", styles["Normal"]))

    # Table data
    data = [["Product", "Price", "Qty", "Total"]]

    for item in order.items.all():
        data.append([
            item.product.title,
            f"₹{item.price}",
            item.quantity,
            f"₹{item.total_price}"
        ])

    data.append(["", "", "Grand Total", f"₹{order.total_amount}"])

    table = Table(data, colWidths=[200, 80, 50, 80])
    table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("ALIGN", (1, 1), (-1, -1), "CENTER"),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))

    elements.append(table)
    doc.build(elements)

    return file_path
