from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), unique=True, nullable=False)
    
    # Core fields
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    # Classification
    priority = db.Column(db.String(20), default='Medium')  # Critical, High, Medium, Low
    status = db.Column(db.String(20), default='Open')      # Open, In Progress, Resolved, Closed
    category = db.Column(db.String(50), default='General') # Malware, DDoS, Phishing, etc
    
    # Source
    source = db.Column(db.String(50), default='Manual')    # AI Firewall, PCAP Analyser, Manual
    source_ip = db.Column(db.String(50), nullable=True)
    
    # Assignment
    department = db.Column(db.String(50), default='SOC Tier 1')
    assigned_to = db.Column(db.String(100), nullable=True)
    issuer = db.Column(db.String(100), nullable=True)
    
    # Location
    location = db.Column(db.String(100), nullable=True)
    
    # Escalation
    escalated = db.Column(db.Boolean, default=False)
    escalation_reason = db.Column(db.Text, nullable=True)
    
    # Remedy
    remedy = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'category': self.category,
            'source': self.source,
            'source_ip': self.source_ip,
            'department': self.department,
            'assigned_to': self.assigned_to,
            'issuer': self.issuer,
            'location': self.location,
            'escalated': self.escalated,
            'escalation_reason': self.escalation_reason,
            'remedy': self.remedy,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None,
        }


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.String(20), db.ForeignKey('tickets.ticket_id'), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }