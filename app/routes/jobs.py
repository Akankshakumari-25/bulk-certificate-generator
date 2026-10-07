from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import Certificate, Job
from app.schemas import CertificateRequest
from app.services.certificate_generator import generate_certificate


router = APIRouter(
    prefix="/api/jobs",
    tags=["Jobs"]
)


def process_job(
    job_id: int,
    certificate_title: str,
    event_name: str
):
    """
    Generate certificates for all recipients in a job.
    Each certificate is processed independently so that
    one failure does not stop the remaining certificates.
    """

    db = SessionLocal()

    try:
        job = db.query(Job).filter(Job.id == job_id).first()

        if not job:
            return

        job.status = "PROCESSING"
        db.commit()

        certificates = (
            db.query(Certificate)
            .filter(Certificate.job_id == job_id)
            .all()
        )

        for certificate in certificates:

            try:
                file_path = generate_certificate(
                    certificate_id=certificate.id,
                    recipient_name=certificate.recipient_name,
                    event_name=event_name,
                    certificate_title=certificate_title
                )

                certificate.status = "SUCCESS"
                certificate.file_path = file_path

                job.successful_count += 1

            except Exception as error:

                certificate.status = "FAILED"
                certificate.error_message = str(error)

                job.failed_count += 1

            db.commit()

        job.completed_at = datetime.utcnow()

        if job.failed_count == 0:
            job.status = "COMPLETED"
        else:
            job.status = "COMPLETED_WITH_ERRORS"

        db.commit()

    finally:
        db.close()


@router.post("/")
def create_job(
    request: CertificateRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # Create a new job
    job = Job(
        status="PENDING",
        total_recipients=len(request.recipients),
        successful_count=0,
        failed_count=0
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    # Create one certificate record for each recipient
    for recipient in request.recipients:

        certificate = Certificate(
            job_id=job.id,
            recipient_name=recipient.name,
            recipient_email=recipient.email,
            status="PENDING"
        )

        db.add(certificate)

    db.commit()

    # Start certificate generation in the background
    background_tasks.add_task(
        process_job,
        job.id,
        request.certificate_title,
        request.event_name
    )

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients
    }
@router.get("/{job_id}")
def get_job_status(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return {
            "error": "Job not found"
        }

    processed = job.successful_count + job.failed_count

    if job.total_recipients > 0:
        progress = round(
            (processed / job.total_recipients) * 100,
            2
        )
    else:
        progress = 0

    return {
        "job_id": job.id,
        "status": job.status,
        "total_recipients": job.total_recipients,
        "successful": job.successful_count,
        "failed": job.failed_count,
        "processed": processed,
        "progress": progress,
        "created_at": job.created_at,
        "completed_at": job.completed_at
    }
@router.get("/{job_id}/certificates")
def get_job_certificates(
    job_id: int,
    db: Session = Depends(get_db)
):
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        return {
            "error": "Job not found"
        }

    certificates = (
        db.query(Certificate)
        .filter(Certificate.job_id == job_id)
        .all()
    )

    return {
        "job_id": job_id,
        "certificates": [
            {
                "id": certificate.id,
                "recipient_name": certificate.recipient_name,
                "recipient_email": certificate.recipient_email,
                "status": certificate.status,
                "download_url": (
                    f"/api/certificates/{certificate.id}"
                    if certificate.status == "SUCCESS"
                    else None
                )
            }
            for certificate in certificates
        ]
    }