import os
import requests
from dotenv import load_dotenv

load_dotenv()

EPIC_BASE_URL = os.getenv("EPIC_BASE_URL")
EPIC_CLIENT_ID = os.getenv("EPIC_CLIENT_ID")

def fetch_patient_fhir(patient_id: str) -> dict:
    """
    Fhir se patient data fetch kro
    return kro patient data se sictionary
    
    """
    try:
        url = f"{EPIC_BASE_URL}/Patient/{patient_id}"

        headers = {
            "ACCEPT": "application/fhir+json",
            "Client-Id": EPIC_CLIENT_ID
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            return {
                "patient_id": patient_id,
                "name": data.get("name", [{}])[0].get("text", "Unknown"),
                "gender": data.get("gender", "Unknown"),
                "birthDate": data.get("birthDate", "Unknown"),
                "status": "success"
        
            }
    
        else:
            return _mock_patient_data(patient_id)
    except Exception as e:
        print(f"Error fetching FHIR data: {e}")
        return _mock_patient_data(patient_id)   


def _mock_patient_data(patient_id: str) -> dict:
    """
    development ky lye fake patient data.
    Real FHIR integration """

    return{
        "patient_id": patient_id,
        "name": "John Doe",
        "gender": "male",
        "birthDate": "1980-01-01",
        "diagnosis": "Type 2 Diabestes",
        "medications": ["Metformin 500mg", "Lisinopril 10mg"],
        "status": "mocked"
  
    }

if __name__ == "__main__":
    result = fetch_patient_fhir("PAT-001")
    print(result)