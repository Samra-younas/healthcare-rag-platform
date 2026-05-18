# claude_client.py
import anthropic
import json
from models import ClinicalSummary
from dotenv import load_dotenv
import os

load_dotenv()

client = anthropic.Anthropic()

CLINICAL_SUMMARY_TOOL = {
    "name": "generate_clinical_summary",
    "description": "Generate a structured clinical summary for a patient query.",
    "input_schema": {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "2-3 sentence clinical summary answering the query"
            },
            "key_findings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of 3-5 key medical findings"
            },
            "recommendations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of 2-3 clinical recommendations"
            },
            "confidence_score": {
                "type": "number",
                "description": "Confidence between 0.0 and 1.0"
            },
            "sources_used": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of source references used"
            }
        },
        "required": ["summary", "key_findings", "recommendations",
                     "confidence_score", "sources_used"]
    }
}


def generate_clinical_summary(
    patient_context: str,
    literature_context: str,
    query: str,
    patient_id: str = "unknown"
) -> ClinicalSummary:

    prompt = f"""You are a clinical decision support assistant.

Patient Context:
{patient_context}

Relevant Medical Literature:
{literature_context}

Query: {query}

Use the generate_clinical_summary tool to provide your response."""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=[CLINICAL_SUMMARY_TOOL],
        tool_choice={"type": "tool", "name": "generate_clinical_summary"},
        messages=[{"role": "user", "content": prompt}]
    )

    for block in response.content:
        if block.type == "tool_use":
            return ClinicalSummary(
                patient_id=patient_id,
                question=query,
                **block.input
            )

    raise ValueError("Claude did not return a tool_use block")