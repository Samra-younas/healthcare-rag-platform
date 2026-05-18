from pydantic import BaseModel
from typing import List, Optional

#___ Input model _____

class PatientQuery(BaseModel):
    patient_id: str #PAT-001
    question: str   # What are the side effects of metformin?

#---- Output model
class ClinicalSummary(BaseModel):
    patient_id: str        # ← required, Claude doesn't fill this
    question: str          # ← required, Claude doesn't fill this
    summary: str
    key_findings: list[str]
    recommendations: list[str]
    confidence_score: float
    sources_used: list[str]