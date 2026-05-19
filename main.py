# main.py
from fastapi import FastAPI, HTTPException
from models import PatientQuery, ClinicalSummary
from graph import graph

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
    try:
        initial_state = {
            "patient_id": request.patient_id,
            "question": request.question,
            "patient_context": "",
            "literature_context": "",
            "summary": None
        }

        config = {"configurable": {"thread_id": request.patient_id}}

        result = graph.invoke(initial_state, config=config)

        return ClinicalSummary(**result["summary"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")