from datetime import datetime
from pathlib import Path

from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas


GENERATED_DIR = Path("generated")
GENERATED_DIR.mkdir(exist_ok=True)


def generate_certificate(
    certificate_id: int,
    recipient_name: str,
    event_name: str,
    certificate_title: str
) -> str:
    
    file_path = GENERATED_DIR / f"certificate_{certificate_id}.pdf"

    page_width, page_height = landscape(A4)

    pdf = canvas.Canvas(
        str(file_path),
        pagesize=(page_width, page_height)
    )

    # Border
    pdf.setLineWidth(3)
    pdf.rect(
        30,
        30,
        page_width - 60,
        page_height - 60
    )

    # Certificate title
    pdf.setFont("Helvetica-Bold", 28)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 120,
        certificate_title
    )

    # Subtitle
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 170,
        "This certificate is proudly presented to"
    )

    # Recipient name
    pdf.setFont("Helvetica-Bold", 30)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 230,
        recipient_name
    )

    # Event text
    pdf.setFont("Helvetica", 16)

    pdf.drawCentredString(
        page_width / 2,
        page_height - 280,
        f"for successfully completing {event_name}"
    )

    # Date
    pdf.setFont("Helvetica", 12)

    pdf.drawCentredString(
        page_width / 2,
        100,
        f"Issued on: {datetime.now().strftime('%d %B %Y')}"
    )

    # Certificate ID
    pdf.drawCentredString(
        page_width / 2,
        75,
        f"Certificate ID: {certificate_id}"
    )

    pdf.save()

    return str(file_path)