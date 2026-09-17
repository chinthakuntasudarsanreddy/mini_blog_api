
from pathlib import Path
from datetime import datetime
from uuid import uuid4

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parents[2]

INVOICE_DIR = BASE_DIR / "media" / "invoices"
INVOICE_DIR.mkdir(parents=True, exist_ok=True)


def generate_invoice_pdf(
    invoice_number: str,
    user_name: str,
    user_email: str,
    plan_name: str,
    amount,
    currency: str,
    started_at: datetime,
    expires_at: datetime,
):
    filename = f"{invoice_number}.pdf"
    pdf_path = INVOICE_DIR / filename

    transaction_id = f"TXN-{uuid4().hex[:12].upper()}"

    pdf = canvas.Canvas(str(pdf_path), pagesize=A4)

    width, height = A4

    # Title
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(
        50,
        height - 60,
        "SUBSCRIPTION INVOICE"
    )

    # Invoice details
    pdf.setFont("Helvetica", 11)

    y = height - 110

    pdf.drawString(
        50,
        y,
        f"Invoice Number: {invoice_number}"
    )

    y -= 22

    pdf.drawString(
        50,
        y,
        f"Transaction ID: {transaction_id}"
    )

    # Customer information
    y -= 45

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        50,
        y,
        "Customer Information"
    )

    pdf.setFont("Helvetica", 11)

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Name: {user_name}"
    )

    y -= 22

    pdf.drawString(
        50,
        y,
        f"Email: {user_email}"
    )

    # Subscription details
    y -= 45

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        50,
        y,
        "Subscription Details"
    )

    pdf.setFont("Helvetica", 11)

    y -= 25

    pdf.drawString(
        50,
        y,
        f"Plan: {plan_name}"
    )

    y -= 22

    pdf.drawString(
        50,
        y,
        f"Price: {currency} {amount}"
    )

    y -= 22

    pdf.drawString(
        50,
        y,
        f"Start Date: {started_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    y -= 22

    pdf.drawString(
        50,
        y,
        f"End Date: {expires_at.strftime('%Y-%m-%d %H:%M:%S')}"
    )

    # Payment status
    y -= 50

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(
        50,
        y,
        "Payment Status: PAID"
    )

    # Footer
    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        50,
        60,
        "Thank you for your subscription."
    )

    pdf.save()

    return str(
        Path("media") / "invoices" / filename
    )
