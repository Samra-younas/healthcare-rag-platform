# graph_state.py
from typing import TypedDict, Optional


class GraphState(TypedDict):
    # --- Input ---
    patient_id: str
    question: str

    # --- Epic OAuth token (optional) ---
    access_token: Optional[str]

    # --- Filled by fetch_fhir node ---
    patient_context: str

    # --- Filled by search_pinecone node ---
    literature_context: str

    # --- Filled by generate_summary node ---
    summary: Optional[dict]

    # --- Filled by write_back node ---
    epic_write_status: Optional[str]