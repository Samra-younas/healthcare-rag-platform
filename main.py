from fastapi import FastAPI
from models import PatientQuery, ClinicalSummary

app = FastAPI(
    title="Healthcare RAG Platform",
    description="FHIR + Pinecone + Claude API — Clinical Summary System",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "Healthcare RAG Platform"
    }

@app.post("/query", response_model=ClinicalSummary)
def query_patient(request: PatientQuery):
    return ClinicalSummary(
        diagnosis="Type 2 Diabetes",
        medications=["Metformin 500mg", "Lisinopril 10mg"],
        summary=f"Patient {request.patient_id} asked: {request.question}",
        sources=["PubMed-2024-001", "FHIR-Patient-Record"],
        confidence=0.91
    )