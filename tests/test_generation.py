from pathlib import Path

from app.services.certificate_generator import generate_certificate


def test_generate_certificate():
    file_path = generate_certificate(
        certificate_id=999,
        recipient_name="Akanksha Kumari",
        event_name="Python Bootcamp 2026",
        certificate_title="Certificate of Completion"
    )

    assert Path(file_path).exists()

    # Clean up the generated test file
    Path(file_path).unlink()