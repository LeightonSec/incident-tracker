# Incident Tracker — SOC Ticketing System

![Version](https://img.shields.io/badge/version-v1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A security incident ticketing system for SOC teams. Engineers raise, triage, assign, escalate and document incidents through a web interface or REST API. Other tools in the LeightonSec SOC Toolkit post tickets automatically when threats are detected.

---

## Ethical Use

This tool is built for legitimate security operations teams to manage real incidents. It is designed for internal deployment on networks you own and operate. Do not deploy it as a publicly accessible service without authentication.

---

## Why This Matters

When a threat is detected, it needs to be tracked, assigned and resolved — not just logged and forgotten. Most small SOC setups lack a lightweight ticketing tool that integrates with their own detection pipeline. This fills that gap: a simple, API-driven incident tracker that other tools can write to automatically, giving analysts a single place to manage every incident from detection through to closure.

---

## Features

- **Full ticket lifecycle** — Open → In Progress → Resolved → Closed
- **REST API** — other tools POST tickets programmatically when threats are detected
- **Priority levels** — Critical, High, Medium, Low
- **Department routing** — SOC Tier 1, SOC Tier 2, Management, IT, Legal
- **Source tracking** — records which tool raised the alert
- **Escalation workflow** — flag tickets for escalation with a reason
- **Comment system** — analysts document investigation progress
- **Auto timestamps** — created, updated and resolved times tracked automatically
- **Live dashboard** — stats update in real time, auto-refreshes every 30 seconds
- **Filtering** — filter by status, priority and source

---

## Setup

```bash
git clone git@github.com:LeightonSec/incident-tracker.git
cd incident-tracker
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
echo "SECRET_KEY=your-secret-key-here" > .env
python3 app.py
```

Open `http://127.0.0.1:5002` in your browser.

---

## REST API

```bash
# Create a ticket
curl -X POST http://127.0.0.1:5002/api/tickets \
  -H "Content-Type: application/json" \
  -d '{"title": "SYN Flood detected", "description": "200 SYN packets from 192.168.1.100", "priority": "High"}'

# List tickets
curl http://127.0.0.1:5002/api/tickets?status=Open
curl http://127.0.0.1:5002/api/tickets?priority=Critical

# Update a ticket
curl -X PUT http://127.0.0.1:5002/api/tickets/INC-20260418-XXXX \
  -H "Content-Type: application/json" \
  -d '{"status": "Resolved", "remedy": "IP blocked at firewall"}'

# Add a comment
curl -X POST http://127.0.0.1:5002/api/tickets/INC-20260418-XXXX/comments \
  -H "Content-Type: application/json" \
  -d '{"author": "analyst", "content": "Investigating source IP"}'

# Dashboard stats
curl http://127.0.0.1:5002/api/stats
```

---

## SOC Toolkit Position

This tool sits in the **Response layer** of the LeightonSec SOC Toolkit:

```
Ingestion  → Intel Pipeline
Detection  → Log Analyser, PCAP Analyser
Analysis   → AI Firewall
Response   → Incident Tracker   ← you are here
Visibility → Unified Dashboard
```

---

## Scope

- Designed for single-team internal use; no multi-tenant support
- No authentication — deploy behind a VPN or firewall, not on the public internet
- SQLite database — not intended for high-volume production deployments

---

## Limitations

- No email or Slack notifications — planned for a future release
- No SLA tracking or breach alerts
- `datetime.utcnow()` deprecation warning under Python 3.12+ — will be addressed in v2
- No user authentication layer

---

## Licence

MIT © Leighton Wilson / LeightonSec
