import os
import sys
import fitz  # PyMuPDF
import re
from datetime import datetime

# Ensure app path works
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from threatapp import create_app, db
from threatapp.models import Threat

app = create_app()
app.app_context().push()

def extract_advisory_text(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def parse_advisory(text):
    try:
        title_line = next(line for line in text.splitlines() if "Vulnerabilities" in line)
        date_line = next(line for line in text.splitlines() if "Original Issue Date" in line)
        severity_line = next(line for line in text.splitlines() if "Severity Rating" in line)

        description_start = text.find("Overview")
        description_end = text.find("Target Audience")
        description = text[description_start:description_end].strip()

        # Normalize severity
        raw = severity_line.split(":")[-1].strip().lower()
        if "critical" in raw or "high" in raw:
            severity = "High"
        elif "medium" in raw:
            severity = "Medium"
        elif "low" in raw:
            severity = "Low"
        else:
            severity = "Medium"

        return {
            "title": title_line.strip(),
            "severity": severity,
            "description": description,
            "date_reported": datetime.strptime(date_line.split(":")[-1].strip(), "%B %d, %Y")
        }

    except Exception as e:
        print(f"[❌] Failed to parse advisory: {e}")
        return None

def save_to_db(data):
    threat = Threat(
        title=data["title"],
        threat_type="CERT-In Advisory",
        severity=data["severity"],
        location="India",
        description=data["description"],
        date_reported=data["date_reported"]
    )
    db.session.add(threat)
    db.session.commit()
    print(f"[✅] Saved: {data['title']}")

if __name__ == "__main__":
    advisory_folder = "data/advisories"
    pdf_files = [f for f in os.listdir(advisory_folder) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print("[ℹ️] No advisory PDFs found.")
    else:
        for file in pdf_files:
            path = os.path.join(advisory_folder, file)
            print(f"[📄] Processing: {file}")
            try:
                text = extract_advisory_text(path)
                data = parse_advisory(text)
                if data:
                    save_to_db(data)
            except Exception as e:
                print(f"[❌] Error reading {file}: {e}")
