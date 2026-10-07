# Bulk Certificate Generator API

A FastAPI-based backend service for generating certificates in bulk, tracking generation progress, handling individual failures, and retrieving generated certificates.

## Features

- Create bulk certificate generation jobs
- Validate recipient information
- Generate certificates using a predefined certificate template
- Process multiple recipients in a single job
- Track job status and progress
- Handle individual certificate failures without stopping the entire job
- Retrieve generated certificates as PDF files
- Store job and certificate information in SQLite
- Automated API and unit tests

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- ReportLab
- Pytest
- HTTPX

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routes/
│   │   ├── jobs.py
│   │   └── certificates.py
│   │
│   └── services/
│       └── certificate_generator.py
│
├── generated/
├── templates/
├── tests/
│   ├── test_generation.py
│   └── test_api.py
│
├── .gitignore
├── requirements.txt
└── README.md
## Setup

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd bulk-certificate-generator

### 2. Create a virtual environment

```bash
python3 -m venv venv

### 3. Activate the virtual environment

For macOS/Linux:

```bash
source venv/bin/activate

For Windows:

```bash
venv\Scripts\activate

### 4. Install dependencies

```bash
pip install -r requirements.txt

## Running the Application

Start the FastAPI server:

```bash
uvicorn app.main:app --reload

## API Endpoints

### Create a Certificate Generation Job

**POST**

```text
/api/jobs/

### Check Job Status

**GET**

```text
/api/jobs/{job_id}

### List Certificates for a Job

**GET**

```text
/api/jobs/{job_id}/certificates

### Retrieve a Certificate

**GET**

```text
/api/certificates/{certificate_id}

## Certificate Generation

Certificates are generated using ReportLab with a predefined certificate layout.

Each certificate contains:

- Certificate title
- Recipient name
- Event name
- Issue date
- Certificate ID

Generated files are stored in the `generated/` directory.

## Failure Handling

Each recipient is processed independently.

If certificate generation fails for one recipient:

- That certificate is marked as `FAILED`
- The error is stored in the database
- The remaining recipients continue processing
- The job is marked as `COMPLETED_WITH_ERRORS`

For example, if 3 certificates are requested and 1 fails:

```text
Total: 3
Successful: 2
Failed: 1
Processed: 3
Progress: 100%

## Database Design

The application uses two main tables:

### Jobs

Stores information about each bulk certificate generation job.

Important fields include:

- Job ID
- Status
- Total recipients
- Successful count
- Failed count
- Creation time
- Completion time

### Certificates

Stores information about individual certificates.

Important fields include:

- Certificate ID
- Job ID
- Recipient name
- Recipient email
- Status
- Generated file path
- Error message

Each certificate belongs to one job.

## Testing

Run all tests using:

```bash
python -m pytest

## Design Decisions

### FastAPI

FastAPI was selected because it provides:

- Simple API development
- Automatic request validation
- Interactive Swagger documentation
- Background task support

### SQLite

SQLite was selected as a lightweight relational database suitable for this assignment. It requires no separate database server and integrates easily with SQLAlchemy.

### SQLAlchemy

SQLAlchemy provides database models and database interaction while keeping the application independent of raw SQL queries.

### BackgroundTasks

FastAPI BackgroundTasks is used to process certificate generation after the job request is accepted.

For a production-scale system, a distributed task queue such as Celery or RQ with Redis could be used instead.

### Failure Isolation

Each certificate is processed inside its own `try/except` block. Therefore, failure of one certificate does not prevent the remaining certificates from being generated.

## Future Improvements

Possible improvements for a production system include:

- Redis/Celery based background processing
- Authentication and authorization
- Persistent job queue
- Better certificate templates
- Cloud object storage for generated PDFs
- Pagination for large certificate lists
- Structured logging
- Database migrations using Alembic
- Retry mechanism for failed certificates