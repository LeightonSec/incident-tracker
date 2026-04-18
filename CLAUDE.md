# CLAUDE.md — Incident Tracker

## What This Is
A Flask web application and REST API for SOC incident ticketing.
Engineers raise, triage, assign, escalate and document security 
incidents. Other tools in the LeightonSec SOC Toolkit can POST 
tickets automatically via the API when threats are detected.
Built as part of the LeightonSec SOC Toolkit.

## SOC Toolkit Position
- **Layer:** Response
- **Receives from:** AI Firewall, PCAP Analyser, Log Analyser (via API)
- **Feeds into:** Future Unified Dashboard
- **Gap it fills:** Incident tracking, assignment and resolution workflow

## Architecture
- `app.py` — Flask server, all REST API routes, stats endpoint
- `models.py` — SQLAlchemy models (Ticket, Comment), to_dict() serialisation
- `templates/index.html` — Dashboard, ticket list, filters, stats, create modal
- `templates/ticket.html` — Ticket detail, update form, comments, escalation
- `instance/incidents.db` — SQLite database (gitignored)

## Current Status
✅ Complete and live — LeightonSec/incident-tracker
✅ Full ticket lifecycle — Open → In Progress → Resolved → Closed
✅ REST API — GET, POST, PUT, DELETE tickets
✅ Comment system
✅ Escalation workflow
✅ Department routing
✅ Source tracking — which tool raised the alert
✅ Auto ticket ID generation — INC-YYYYMMDD-XXXX
✅ Auto resolved_at timestamp when status → Resolved
✅ Stats dashboard with live counts
✅ Filtering by status, priority, source
✅ Auto-refresh every 30 seconds

## API Endpoints
- `GET /api/tickets` — list all tickets (supports ?status=, ?priority=, ?source=, ?department=)
- `POST /api/tickets` — create ticket (requires title, description)
- `GET /api/tickets/<id>` — get ticket with comments
- `PUT /api/tickets/<id>` — update ticket (whitelist of allowed fields)
- `DELETE /api/tickets/<id>` — delete ticket
- `POST /api/tickets/<id>/comments` — add comment
- `GET /api/stats` — dashboard statistics

## Valid Values
- **Priority:** Critical, High, Medium, Low
- **Status:** Open, In Progress, Resolved, Closed
- **Department:** SOC Tier 1, SOC Tier 2, Management, IT, Legal
- **Source:** Manual, AI Firewall, PCAP Analyser, Log Analyser, Intel Pipeline

## Known Issues / Gotchas
- `datetime.utcnow()` deprecation warning — fix in v2 with `datetime.now(datetime.UTC)`
- SQLite database created in `instance/` folder by Flask-SQLAlchemy — gitignored via `*.db` and `instance/`
- SECRET_KEY default is `changethiskey` — must be changed in production
- No authentication — anyone with network access can create/modify tickets
- Comment author defaults to 'Anonymous' if not provided

## Next Steps
- [ ] Auto-integration with AI Firewall — POST ticket on JAILBREAK verdict
- [ ] Auto-integration with PCAP Analyser — POST ticket on HIGH severity
- [ ] Email/Slack notifications on Critical tickets
- [ ] User authentication layer
- [ ] SLA tracking — breach alerts
- [ ] PDF export
- [ ] Docker containerisation
- [ ] Unified Dashboard integration

## Tech Stack
- Python, Flask, Flask-SQLAlchemy
- SQLite database
- python-dotenv

## Security Rules
- SECRET_KEY in .env — never committed
- *.db and instance/ gitignored