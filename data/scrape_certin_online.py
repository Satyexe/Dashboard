# data/scrape_certin_online.py

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

# Add app to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from threatapp import create_app, db
from threatapp.models import Threat

Threatapp = create_app()
Threatapp.app_context().push()

BASE_URL = "https://www.cert-in.org.in"
ADVISORY_URL = "https://www.cert-in.org.in/advisory/"

def get_advisory_links():
    res = requests.get(ADVISORY_URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    links = []
    for a in soup.select('a[href*="advisory"]'):
        href = a.get('href')
        if "advisory/" in href and href.endswith(".htm"):
            full_url = BASE_URL + "/" + href
            links.append(full_url)
    return list(set(links))

def parse_advisory_page(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    text = soup.get_text()

    try:
        title = soup.find("h1").text.strip()
        date_line = next(line for line in text.splitlines() if "Original Issue Date" in line)
        severity_line = next(line for line in text.splitlines() if "Severity Rating" in line)

        description_start = text.find("Overview")
        description_end = text.find("Target Audience")
        description = text[description_start:description_end].strip()

        raw = severity_line.split(":")[-1].strip().lower()
        if "critical" in raw or "high" in raw:
            severity = "High"
        elif "medium" in raw:
            severity = "Medium"
        elif "low" in raw:
            severity = "Low"
        else:
            severity = "Medium"

        date_str = date_line.split(":")[-1].strip()
        date_obj = datetime.strptime(date_str, "%B %d, %Y")

        return {
            "title": title,
            "severity": severity,
            "description": description,
            "date_reported": date_obj
        }
    except Exception as e:
        print(f"[❌] Failed to parse {url}: {e}")
        return None

def save_to_db(data):
    exists = Threat.query.filter_by(title=data["title"]).first()
    if exists:
        print(f"[ℹ️] Skipped duplicate: {data['title']}")
        return
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
    print(f"[✅] Added: {data['title']}")

if __name__ == "__main__":
    print("[🔎] Fetching advisory links...")
    links = get_advisory_links()
    print(f"[📄] Found {len(links)} advisories")

    for link in links:
        print(f"[➡️] Parsing: {link}")
        data = parse_advisory_page(link)
        if data:
            save_to_db(data)
