import uuid
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import TableStyle
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
import os

import os
import uuid
from datetime import datetime
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def generate_invoice_pdf(data):
    """
    booking: dict (booking data)
    user: dict (customer data)
    company: dict (company data)
    """
    
    booking = data["booking_details"]
    user = data.booking_details.user
    company = data.hotel
    invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

    # Create invoices folder
    invoice_dir = "invoices"
    os.makedirs(invoice_dir, exist_ok=True)

    file_path = os.path.join(invoice_dir, f"{invoice_number}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # ---------------------------
    # Company Header
    # ---------------------------
    elements.append(Paragraph(f"<b>{company['name']}</b>", styles["Title"]))
    elements.append(Paragraph(company["address"], styles["Normal"]))
    elements.append(Paragraph(f"GSTIN: {company['gst']}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 0.2 * inch))

    # ---------------------------
    # Invoice Info
    # ---------------------------
    elements.append(Paragraph(f"<b>Invoice No:</b> {invoice_number}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Booking ID:</b> {booking['id']}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}", styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------------------
    # Billing Details
    # ---------------------------
    elements.append(Paragraph("<b>Bill To:</b>", styles["Heading2"]))
    elements.append(Paragraph(user["name"], styles["Normal"]))
    elements.append(Paragraph(user["billing_address"].replace("\n", "<br/>"), styles["Normal"]))
    elements.append(Paragraph(user["email"], styles["Normal"]))
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------------------
    # Booking Table
    # ---------------------------
    table_data = [
        ["Description", "Unit Price", "Qty", "Total"],
        [
            f"{booking['room_type']} - {booking['hotel_name']}",
            f"₹ {booking['price_per_night']}",
            booking["nights"],
            f"₹ {booking['subtotal']}"
        ]
    ]

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (1, 1), (-1, -1), 'CENTER')
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # ---------------------------
    # Price Summary
    # ---------------------------
    elements.append(Paragraph("<b>Price Summary</b>", styles["Heading2"]))
    elements.append(Paragraph(f"Subtotal: ₹ {booking['subtotal']}", styles["Normal"]))
    elements.append(Paragraph(f"Discount: -₹ {booking['discount']}", styles["Normal"]))
    elements.append(Paragraph(f"GST (18%): ₹ {round(booking['tax'], 2)}", styles["Normal"]))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(f"<b>Total Amount: ₹ {round(booking['total'], 2)}</b>", styles["Heading1"]))

    doc.build(elements)

    return invoice_number, file_path
