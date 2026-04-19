# ⚡ Incident Tracker — SOC Ticketing System

A security incident ticketing system that brings together incident response across departments. Engineers can raise, triage, assign, escalate and document incidents through a clean web interface or via REST API — allowing other tools in the LeightonSec SOC Toolkit to automatically create tickets when threats are detected.

---

## What It Does

When a threat is detected — by the AI Firewall, PCAP Analyser or Log Analyser — it needs to be tracked, assigned and resolved. The Incident Tracker provides the response layer of the SOC Toolkit, giving analysts a centralised place to manage every incident from detection through to resolution.

---

## Features

- **Web interface** — create, view, update and close tickets through the browser
- **REST API** — other tools can POST tickets programmatically when threats are detected
- **Full ticket lifecycle** — Open → In Progress → Resolved → Closed
- **Priority levels** — Critical, High, Medium, Low
- **Department routing** — SOC Tier 1, SOC Tier 2, Management, IT, Legal
- **Source tracking** — which tool raised the alert
- **Escalation workflow** — flag tickets for escalation with reason
- **Remedy documentation** — record actions taken to resolve
- **Comment system** — analysts can document investigation progress
- **Auto timestamps** — created, updated and resolved times tracked automatically
- **Live dashboard** — stats update in real time, auto-refreshes every 30 seconds
- **Filtering** — filter by status, priority and source

---

## Ticket Structure

Every ticket contains:

| Field | Description |
|-------|-------------|
| Ticket ID | Auto-generated unique reference (INC-YYYYMMDD-XXXX) |
| Title | Brief incident description |
| Description | Full incident detail |
| Priority | Critical / High / Medium / Low |
| Status | Open / In Progress / Resolved / Closed |
| Category | Malware, DDoS, Phishing, Port Scan, etc |
| Source | Which tool detected the incident |
| Source IP | Offending IP address |
| Department | Responsible team |
| Assigned To | Owning analyst |
| Issuer | Who raised the ticket |
| Location | Affected location |
| Escalated | Whether ticket has been escalated |
| Escalation Reason | Why it was escalated |
| Remedy | Actions taken to resolve |
| Comments | Investigation audit trail |
| Timestamps | Created, updated, resolved |

---

## REST API

### Create a ticket
```bash
curl -X POST http://127.0.0.1:5002/api/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "title": "SYN Flood detected",
    "description": "200 SYN packets from 192.168.1.100",
    "priority": "High",
    "category": "DDoS",
    "source": "PCAP Analyser",
    "source_ip": "192.168.1.100",
    "department": "SOC Tier 1"
  }'
```

### Get all tickets
```bash
curl http://127.0.0.1:5002/api/tickets
curl http://127.0.0.1:5002/api/tickets?status=Open
curl http://127.0.0.1:5002/api/tickets?priority=Critical
```

### Update a ticket
```bash
curl -X PUT http://127.0.0.1:5002/api/tickets/INC-20260418-XXXX \
  -H "Content-Type: application/json" \
  -d '{"status": "Resolved", "remedy": "IP blocked at firewall"}'
```

### Add a comment
```bash
curl -X POST http://127.0.0.1:5002/api/tickets/INC-20260418-XXXX/comments \
  -H "Content-Type: application/json" \
  -d '{"author": "Leighton", "content": "Investigating source IP"}'
```

---

## Setup

**Requirements:** Python 3.x

```bash
# Clone the repo
git clone git@github.com:LeightonSec/incident-tracker.git
cd incident-tracker

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set secret key
echo "SECRET_KEY=your-secret-key-here" > .env

# Run the server
python3 app.py
```

Then open `http://127.0.0.1:5002` in your browser.

---

## Project Structure

incident-tracker/
├── app.py          # Flask server, REST API routes
├── models.py       # SQLAlchemy database models (Ticket, Comment)
├── templates/
│   ├── index.html  # Dashboard — ticket list, stats, filters
│   └── ticket.html # Ticket detail — update, comments, escalation
├── requirements.txt
└── .env            # Secret key (never committed)

---

## SOC Toolkit Position

This tool sits in the **Response layer** of the LeightonSec SOC Toolkit:

Ingestion    → Intel Pipeline
Detection    → Log Analyser + PCAP Analyser
Analysis     → AI Firewall
Response     → Incident Tracker ← you are here
Visibility   → Unified Dashboard (planned)

**Integration points:**
- PCAP Analyser HIGH severity → auto POST ticket
- AI Firewall JAILBREAK verdict → auto POST ticket
- Log Analyser suspicious IP → auto POST ticket

---

## Roadmap

- [ ] Email/Slack notifications on Critical tickets
- [ ] SLA tracking — time to respond and resolve
- [ ] Auto-integration with AI Firewall and PCAP Analyser
- [ ] User authentication
- [ ] Ticket export as PDF
- [ ] Docker containerisation
- [ ] Unified Dashboard integration

---

## Author

**Leighton Wilson** —  SOC Analyst | LeightonSec 
[LeightonSec GitHub](https://github.com/LeightonSec)

---

*Built as part of a hands-on cybersecurity portfolio. Part of the LeightonSec SOC Toolkit.*