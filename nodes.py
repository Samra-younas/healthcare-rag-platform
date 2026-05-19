# nodes.py
from graph_state import GraphState
from fhir_client import fetch_patient_fhir, write_summary_to_epic
from pinecone_client import search_medical_literature
from claude_client import generate_clinical_summary


def fetch_fhir(state: GraphState) -> GraphState:
    """Node 1 — Fetch patient data from Epic FHIR"""
    patient_data = fetch_patient_fhir(
        patient_id=state["patient_id"],
        access_token=state.get("access_token")  # real token or None → mock
    )

    patient_context = f"""
Patient ID: {patient_data['patient_id']}
Name: {patient_data['name']}
Gender: {patient_data['gender']}
Date of Birth: {patient_data['birthDate']}
Diagnosis: {patient_data['diagnosis']}
Medications: {', '.join(patient_data['medications'])}
Data Source: {patient_data['status']}
""".strip()

    return {"patient_context": patient_context}


def search_pinecone(state: GraphState) -> GraphState:
    """Node 2 — Search medical literature in Pinecone"""
    results = search_medical_literature(state["question"])

    literature_context = "\n".join([
        f"- {match['text']} (source: {match['source']})"
        for match in results
    ])

    return {"literature_context": literature_context}


def generate_summary(state: GraphState) -> GraphState:
    """Node 3 — Call Claude to generate structured summary"""
    result = generate_clinical_summary(
        patient_context=state["patient_context"],
        literature_context=state["literature_context"],
        query=state["question"],
        patient_id=state["patient_id"]
    )

    return {"summary": result.model_dump()}


def write_to_epic(state: GraphState) -> GraphState:
    """Node 4 — Write AI summary back to Epic (if token available)"""
    token = state.get("access_token")

    if not token:
        return {"epic_write_status": "skipped — no token provided"}

    summary_text = state["summary"].get("summary", "")

    result = write_summary_to_epic(
        patient_id=state["patient_id"],
        summary=summary_text,
        access_token=token
    )

    return {"epic_write_status": result["status"]}