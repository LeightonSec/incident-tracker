import os
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from models import db, Ticket, Comment

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'changeme')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///incidents.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

def generate_ticket_id():
    """Generate unique ticket ID — format: INC-YYYYMMDD-XXXX"""
    date = datetime.utcnow().strftime("%Y%m%d")
    unique = str(uuid.uuid4())[:4].upper()
    return f"INC-{date}-{unique}"

# ── Web Interface ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ticket/<ticket_id>')
def ticket_detail(ticket_id):
    return render_template('ticket.html', ticket_id=ticket_id)

# ── Ticket API ────────────────────────────────────────────────────────────────

@app.route('/api/tickets', methods=['GET'])
def get_tickets():
    """Get all tickets with optional filtering"""
    status = request.args.get('status')
    priority = request.args.get('priority')
    source = request.args.get('source')
    department = request.args.get('department')

    query = Ticket.query

    if status:
        query = query.filter_by(status=status)
    if priority:
        query = query.filter_by(priority=priority)
    if source:
        query = query.filter_by(source=source)
    if department:
        query = query.filter_by(department=department)

    tickets = query.order_by(Ticket.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets])

@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    """Create a new ticket"""
    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    required = ['title', 'description']
    for field in required:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400

    # Validate priority
    valid_priorities = ['Critical', 'High', 'Medium', 'Low']
    priority = data.get('priority', 'Medium')
    if priority not in valid_priorities:
        return jsonify({"error": f"Invalid priority. Must be one of: {valid_priorities}"}), 400

    # Validate status
    valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    status = data.get('status', 'Open')
    if status not in valid_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {valid_statuses}"}), 400

    ticket = Ticket(
        ticket_id=generate_ticket_id(),
        title=data['title'][:200],
        description=data['description'],
        priority=priority,
        status=status,
        category=data.get('category', 'General'),
        source=data.get('source', 'Manual'),
        source_ip=data.get('source_ip'),
        department=data.get('department', 'SOC Tier 1'),
        assigned_to=data.get('assigned_to'),
        issuer=data.get('issuer'),
        location=data.get('location'),
        escalated=data.get('escalated', False),
        escalation_reason=data.get('escalation_reason'),
        remedy=data.get('remedy')
    )

    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201

@app.route('/api/tickets/<ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    """Get a specific ticket"""
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    
    comments = Comment.query.filter_by(ticket_id=ticket_id).order_by(Comment.created_at.asc()).all()
    result = ticket.to_dict()
    result['comments'] = [c.to_dict() for c in comments]
    return jsonify(result)

@app.route('/api/tickets/<ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    """Update a ticket"""
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Update allowed fields
    allowed = ['title', 'description', 'priority', 'status', 'category',
               'department', 'assigned_to', 'issuer', 'location',
               'escalated', 'escalation_reason', 'remedy']

    for field in allowed:
        if field in data:
            setattr(ticket, field, data[field])

    # Auto set resolved_at when status changes to Resolved
    if data.get('status') == 'Resolved' and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()

    ticket.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify(ticket.to_dict())

@app.route('/api/tickets/<ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    """Delete a ticket"""
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()
    return jsonify({"message": f"Ticket {ticket_id} deleted"})

# ── Comments API ──────────────────────────────────────────────────────────────

@app.route('/api/tickets/<ticket_id>/comments', methods=['POST'])
def add_comment(ticket_id):
    """Add a comment to a ticket"""
    ticket = Ticket.query.filter_by(ticket_id=ticket_id).first()
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({"error": "Comment content required"}), 400

    comment = Comment(
        ticket_id=ticket_id,
        author=data.get('author', 'Anonymous'),
        content=data['content']
    )

    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_dict()), 201

# ── Stats API ─────────────────────────────────────────────────────────────────

@app.route('/api/stats')
def get_stats():
    """Dashboard statistics"""
    total = Ticket.query.count()
    open_tickets = Ticket.query.filter_by(status='Open').count()
    in_progress = Ticket.query.filter_by(status='In Progress').count()
    resolved = Ticket.query.filter_by(status='Resolved').count()
    critical = Ticket.query.filter_by(priority='Critical').count()
    escalated = Ticket.query.filter(Ticket.escalated == True).count()

    return jsonify({
        'total': total,
        'open': open_tickets,
        'in_progress': in_progress,
        'resolved': resolved,
        'critical': critical,
        'escalated': escalated
    })

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=5002)