import requests, base64, time
from flask import Flask, request, session, redirect, url_for
from datetime import datetime, timezone

app = Flask(__name__)
app.secret_key = "clinical_v18_final"

# --- CONFIGURATION ---
CLIENT_ID = 
REDIRECT_URI = 
TOKEN_URL = 
AUTH_URL = 
FHIR_URL = 

# --- NEW HELPER: Fetch Name, DOB, Gender ---
def get_patient_info(token, p_id):
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"}
    try:
        res = requests.get(f"{FHIR_URL}/Patient/{p_id}", headers=headers)
        if res.status_code == 200:
            p = res.json()
            names = p.get('name', [{}])[0]
            return {
                "name": f"{names.get('given',[''])[0]} {names.get('family','')}",
                "dob": p.get('birthDate', 'N/A'),
                "gender": p.get('gender', 'N/A').capitalize()
            }
    except: return None

@app.route("/")
def home():
    state_id = str(int(time.time()))
    params = {"response_type": "code", "client_id": CLIENT_ID, "redirect_uri": REDIRECT_URI, "scope": "openid fhirUser user/Patient.read user/DocumentReference.write user/Encounter.read", "state": state_id, "aud": FHIR_URL}
    target_url = f"{AUTH_URL}?" + requests.compat.urlencode(params)
    return f"<div style='text-align:center; margin-top:100px; font-family:sans-serif;'><h1>🏥 Epic Practitioner Portal</h1><a href='{target_url}'>LOGIN</a></div>"

@app.route("/callback")
def callback():
    code = request.args.get("code")
    r = requests.post(TOKEN_URL, data={"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECT_URI, "client_id": CLIENT_ID})
    if "access_token" in r.json():
        session['token'] = r.json().get("access_token")
        return redirect(url_for('dashboard'))
    return "Login Failed."

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    token = session.get('token')
    if not token: return redirect(url_for('home'))
    
    selected_p_id = request.form.get('v_id') or request.args.get('p_id') or "e3MBXCOmcoLKl7ayLD51AWA3" 
    info = get_patient_info(token, selected_p_id) # Fetch details for Blue Box
    
    patients = [{'id': '', 'name': 'Jason Argus'}, {'id': 'erXuFYUfucBZaryVksYEcMg3', 'name': 'Camila Lopez'}]
    options = "".join([f"<option value='{p['id']}' {'selected' if p['id']==selected_p_id else ''}>{p['name']}</option>" for p in patients])
    
    return f"""
    <div style="max-width:900px; margin:auto; font-family:sans-serif; padding:20px; border:1px solid #eee; border-radius:15px; margin-top:20px;">
        <h2 style="color:#007bff; border-bottom:3px solid #007bff; padding-bottom:10px;">🏥 Patient Clinical Dashboard</h2>
        
        <div style="background:#f1f8ff; padding:20px; border-radius:10px; margin-bottom:25px; display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h3 style="margin:0; color:#0056b3;">{info['name'] if info else 'Loading...'}</h3>
                <p style="margin:5px 0;"><b>DOB:</b> {info['dob'] if info else 'N/A'} | <b>Gender:</b> {info['gender'] if info else 'N/A'}</p>
                <p style="margin:0; font-size:12px; color:#666;">FHIR ID: {selected_p_id}</p>
            </div>
            <form action="/dashboard" method="POST">
                <select name="v_id" onchange="this.form.submit()" style="padding:10px; border-radius:5px; border:1px solid #007bff;">{options}</select>
            </form>
        </div>

        <div style="border:1px solid #28a745; padding:20px; border-radius:10px; margin-bottom:30px;">
            <h4 style="color:#28a745; margin-top:0;">📝 Step 1: Write Note</h4>
            <form action="/push_note" method="POST">
                <input type="hidden" name="p_id" value="{selected_p_id}">
                <textarea name="note_text" style="width:98%; height:60px; margin-bottom:15px;">Clinical Test Note - {datetime.now().strftime('%H:%M')}</textarea>
                <button type="submit" style="width:100%; padding:15px; background:#28a745; color:white; border:none; border-radius:5px; font-weight:bold; cursor:pointer;">PUSH TO EPIC DATABASE</button>
            </form>
        </div>

        <h4 style="color:blue;">🔍 Step 2: Live Verification Table</h4>
        {fetch_history_html(token, selected_p_id)}
    </div>
    """

def fetch_history_html(token, p_id):
    try:
        res = requests.get(f"{FHIR_URL}/DocumentReference?patient={p_id}&_sort=-date", headers={"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"})
        if res.status_code == 200:
            entries = res.json().get('entry', [])
            if not entries: return "<p>No records found.</p>"
            html = "<table border='1' style='width:100%; border-collapse:collapse; font-size:13px;'>"
            html += "<tr style='background:#f1f3f5;'><th>Time (UTC)</th><th>Unique Resource ID</th><th>Linked Visit (Encounter)</th><th>Status</th></tr>"
            for e in entries:
                r = e.get('resource', {})
                res_id, date, status = r.get('id', 'N/A'), r.get('date', 'N/A'), r.get('docStatus', 'final')
                enc_id = r.get('context', {}).get('encounter', [{}])[0].get('reference', 'N/A').replace('Encounter/', '')
                html += f"<tr><td style='padding:8px;'>{date}</td><td style='padding:8px; color:#0056b3;'>{res_id}</td><td style='padding:8px;'>{enc_id}</td><td style='padding:8px;'>{status}</td></tr>"
            return html + "</table>"
    except: return "Error fetching table."

@app.route("/push_note", methods=['POST'])
def push_note():
    token = session.get('token')
    p_id = request.form.get('p_id')
    note_text = request.form.get('note_text')
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # --- EXACT SAME LOGIC AS YOUR STEP 1, 2, 3 ---
    enc_id = "eP9Y6p55Z6.t.HcyX.6v8Sg3" 
    try:
        enc_res = requests.get(f"{FHIR_URL}/Encounter?patient={p_id}&_count=1", headers={"Authorization": f"Bearer {token}", "Accept": "application/fhir+json"})
        if enc_res.status_code == 200 and enc_res.text.strip():
            entries = enc_res.json().get('entry', [])
            if entries: enc_id = entries[0].get('resource', {}).get('id')
    except: pass

    payload = {
        "resourceType": "DocumentReference", "status": "current", "docStatus": "final",
        "category": [{"coding": [{"system": "http://hl7.org/fhir/us/core/CodeSystem/us-core-documentreference-category", "code": "clinical-note", "display": "Clinical Note"}]}],
        "type": {"coding": [{"system": "http://loinc.org", "code": "11488-4"}]},
        "subject": {"reference": f"Patient/{p_id}"}, "date": now,
        "content": [{"attachment": {"contentType": "text/plain", "data": base64.b64encode(note_text.encode()).decode()}}],
        "context": {"encounter": [{"reference": f"Encounter/{enc_id}"}], "period": {"start": now}}
    }

    try:
        res = requests.post(f"{FHIR_URL}/DocumentReference", json=payload, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/fhir+json"})
        if res.status_code == 201:
            return f"<div style='text-align:center; padding:50px;'><h1>✅ 201 Created</h1><a href='/dashboard?p_id={p_id}'>Return to Dashboard</a></div>"
        return f"Error {res.status_code}: {res.text}"
    except Exception as e: return str(e)

if __name__ == "__main__":
    app.run(port=5000, debug=True)