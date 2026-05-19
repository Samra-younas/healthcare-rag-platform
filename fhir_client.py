# fhir_client.py
import os
import base64
import requests
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

FHIR_URL = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4"
EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID")


# ─────────────────────────────────────────
# READ — Fetch Patient from Epic
# ─────────────────────────────────────────
def fetch_patient_fhir(patient_id: str, access_token: str = None) -> dict:
    """
    Epic FHIR sandbox se real patient data fetch karo.
    If token missing → mock data return karo.
    """
    if not access_token:
        return _mock_patient_data(patient_id)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/fhir+json"
    }

    try:
        # --- Fetch basic patient info ---
        res = requests.get(
            f"{FHIR_URL}/Patient/{patient_id}",
            headers=headers
        )

        if res.status_code != 200:
            print(f"Epic returned {res.status_code} — using mock")
            return _mock_patient_data(patient_id)

        p = res.json()
        names = p.get('name', [{}])[0]
        full_name = f"{names.get('given', [''])[0]} {names.get('family', '')}".strip()

        # --- Fetch conditions ---
        conditions = []
        cond_res = requests.get(
            f"{FHIR_URL}/Condition?patient={patient_id}",
            headers=headers
        )
        if cond_res.status_code == 200:
            for entry in cond_res.json().get('entry', []):
                text = entry.get('resource', {}).get('code', {}).get('text', '')
                if text:
                    conditions.append(text)

        # --- Fetch medications ---
        medications = []
        med_res = requests.get(
            f"{FHIR_URL}/MedicationRequest?patient={patient_id}",
            headers=headers
        )
        if med_res.status_code == 200:
            for entry in med_res.json().get('entry', []):
                text = entry.get('resource', {}).get(
                    'medicationCodeableConcept', {}
                ).get('text', '')
                if text:
                    medications.append(text)

        return {
            "patient_id": patient_id,
            "name": full_name,
            "gender": p.get('gender', 'Unknown'),
            "birthDate": p.get('birthDate', 'Unknown'),
            "diagnosis": ', '.join(conditions) if conditions else "See medical record",
            "medications": medications if medications else ["See medication list"],
            "status": "epic_sandbox"
        }

    except Exception as e:
        print(f"FHIR fetch error: {e}")
        return _mock_patient_data(patient_id)


# ─────────────────────────────────────────
# WRITE — Push AI Summary to Epic
# ─────────────────────────────────────────
def write_summary_to_epic(
    patient_id: str,
    summary: str,
    access_token: str
) -> dict:
    """
    Claude ka generated summary Epic mein
    DocumentReference ki tarah write karo.
    """
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/fhir+json"
    }

    # --- Get latest encounter ID ---
    enc_id = None
    try:
        enc_res = requests.get(
            f"{FHIR_URL}/Encounter?patient={patient_id}&_count=1",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/fhir+json"
            }
        )
        if enc_res.status_code == 200:
            entries = enc_res.json().get('entry', [])
            if entries:
                enc_id = entries[0].get('resource', {}).get('id')
    except Exception as e:
        print(f"Encounter fetch error: {e}")

    # --- Build FHIR DocumentReference payload ---
    payload = {
        "resourceType": "DocumentReference",
        "status": "current",
        "docStatus": "final",
        "category": [{
            "coding": [{
                "system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category",
                "code": "clinical-note",
                "display": "Clinical Note"
            }]
        }],
        "type": {
            "coding": [{
                "system": "http://loinc.org",
                "code": "11488-4",
                "display": "Consult note"
            }]
        },
        "subject": {"reference": f"Patient/{patient_id}"},
        "date": now,
        "content": [{
            "attachment": {
                "contentType": "text/plain",
                "data": base64.b64encode(summary.encode()).decode()
            }
        }]
    }

    # --- Add encounter context if found ---
    if enc_id:
        payload["context"] = {
            "encounter": [{"reference": f"Encounter/{enc_id}"}],
            "period": {"start": now}
        }

    # --- Push to Epic ---
    try:
        res = requests.post(
            f"{FHIR_URL}/DocumentReference",
            json=payload,
            headers=headers
        )
        if res.status_code == 201:
            return {
                "status": "success",
                "resource_id": res.json().get('id', 'unknown'),
                "message": "Summary written to Epic successfully"
            }
        else:
            return {
                "status": "failed",
                "code": res.status_code,
                "message": res.text
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


# ─────────────────────────────────────────
# MOCK — Fallback Data for Development
# ─────────────────────────────────────────
def _mock_patient_data(patient_id: str) -> dict:
    """
    Real token nahi hai to ye mock data use karo.
    Epic Sandbox architecture same hai — sirf data fake hai.
    """
    mock_patients = {
        "e3MBXCOmcoLKl7ayLD51AWA3": {
            "patient_id": "e3MBXCOmcoLKl7ayLD51AWA3",
            "name": "Jason Argus",
            "gender": "male",
            "birthDate": "1985-03-15",
            "diagnosis": "Type 2 Diabetes, Hypertension",
            "medications": ["Metformin 500mg", "Lisinopril 10mg"],
            "status": "mocked"
        },
        "erXuFYUfucBZaryVksYEcMg3": {
            "patient_id": "erXuFYUfucBZaryVksYEcMg3",
            "name": "Camila Lopez",
            "gender": "female",
            "birthDate": "1990-07-22",
            "diagnosis": "Asthma, Anxiety",
            "medications": ["Albuterol inhaler", "Sertraline 50mg"],
            "status": "mocked"
        }
    }
    return mock_patients.get(patient_id, {
        "patient_id": patient_id,
        "name": "Unknown Patient",
        "gender": "Unknown",
        "birthDate": "Unknown",
        "diagnosis": "Unknown",
        "medications": ["Unknown"],
        "status": "mocked"
    })


# ─────────────────────────────────────────
# TEST
# ─────────────────────────────────────────
if __name__ == "__main__":
    # Test mock fetch
    result = fetch_patient_fhir("e3MBXCOmcoLKl7ayLD51AWA3")
    print("FETCH RESULT:", result)