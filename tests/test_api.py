from unittest.mock import patch
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_job():
    response = client.post(
        "/api/jobs/",
        json={
            "certificate_title": "Certificate of Completion",
            "event_name": "Python Bootcamp 2026",
            "recipients": [
                {
                    "name": "Akanksha Kumari",
                    "email": "akanksha@gmail.com"
                },
                {
                    "name": "Rahul Sharma",
                    "email": "rahul@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["total_recipients"] == 2
def test_invalid_email():
    response = client.post(
        "/api/jobs/",
        json={
            "certificate_title": "Certificate of Completion",
            "event_name": "Python Bootcamp 2026",
            "recipients": [
                {
                    "name": "Akanksha Kumari",
                    "email": "not-an-email"
                }
            ]
        }
    )

    assert response.status_code == 422
def test_job_status():
    create_response = client.post(
        "/api/jobs/",
        json={
            "certificate_title": "Certificate of Completion",
            "event_name": "Python Bootcamp 2026",
            "recipients": [
                {
                    "name": "Akanksha Kumari",
                    "email": "akanksha@gmail.com"
                }
            ]
        }
    )

    assert create_response.status_code == 200

    job_id = create_response.json()["job_id"]

    status_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["job_id"] == job_id
    assert data["total_recipients"] == 1
    assert data["processed"] == 1
    assert data["progress"] == 100
def test_individual_certificate_failure():
    def fake_generate_certificate(
        certificate_id,
        recipient_name,
        event_name,
        certificate_title
    ):
        if recipient_name == "Fail Test":
            raise Exception("Simulated failure")

        return f"generated/test_{certificate_id}.pdf"

    with patch(
        "app.routes.jobs.generate_certificate",
        side_effect=fake_generate_certificate
    ):
        response = client.post(
            "/api/jobs/",
            json={
                "certificate_title": "Certificate of Completion",
                "event_name": "Python Bootcamp 2026",
                "recipients": [
                    {
                        "name": "Akanksha Kumari",
                        "email": "akanksha@gmail.com"
                    },
                    {
                        "name": "Fail Test",
                        "email": "fail@example.com"
                    },
                    {
                        "name": "Rahul Sharma",
                        "email": "rahul@gmail.com"
                    }
                ]
            }
        )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    status_response = client.get(
        f"/api/jobs/{job_id}"
    )

    assert status_response.status_code == 200

    data = status_response.json()

    assert data["total_recipients"] == 3
    assert data["successful"] == 2
    assert data["failed"] == 1
    assert data["processed"] == 3
    assert data["progress"] == 100
    assert data["status"] == "COMPLETED_WITH_ERRORS"
def test_certificate_retrieval():
    response = client.post(
        "/api/jobs/",
        json={
            "certificate_title": "Certificate of Completion",
            "event_name": "Python Bootcamp 2026",
            "recipients": [
                {
                    "name": "Akanksha Kumari",
                    "email": "akanksha@gmail.com"
                }
            ]
        }
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    certificates_response = client.get(
        f"/api/jobs/{job_id}/certificates"
    )

    assert certificates_response.status_code == 200

    certificates = certificates_response.json()["certificates"]

    assert len(certificates) == 1
    assert certificates[0]["status"] == "SUCCESS"

    certificate_id = certificates[0]["id"]

    download_response = client.get(
        f"/api/certificates/{certificate_id}"
    )

    assert download_response.status_code == 200
    assert download_response.headers["content-type"] == "application/pdf"