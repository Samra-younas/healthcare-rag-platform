# test_claude_client.py
from claude_client import generate_clinical_summary

result = generate_clinical_summary(
    patient_context="Patient: 45yo male, Type 2 Diabetes, HbA1c: 8.2%",
    literature_context="Studies show metformin remains first-line therapy for T2DM.",
    query="What medication adjustments should be considered?"
)

print(result.model_dump_json(indent=2))