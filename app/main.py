from fastapi import FastAPI

from app.database import Base, engine
from app import models
from app.routes.jobs import router as jobs_router
from app.routes.certificates import router as certificates_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Bulk Certificate Generator API",
    description="API for generating and tracking certificates in bulk.",
    version="1.0.0"
)

app.include_router(jobs_router)
app.include_router(certificates_router)

@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }