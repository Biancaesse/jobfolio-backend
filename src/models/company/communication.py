from src.models.user import db
from datetime import datetime

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # "user" o "company"
    sender_id = db.Column(db.Integer, nullable=False)  # user_id o company_user_id
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<Message {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_type': self.sender_type,
            'sender_id': self.sender_id,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=True)
    subject = db.Column(db.String(100), nullable=True)
    is_archived_by_user = db.Column(db.Boolean, default=False)
    is_archived_by_company = db.Column(db.Boolean, default=False)
    last_message_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relazioni
    messages = db.relationship('Message', backref='conversation', lazy=True)
    
    def __repr__(self):
        return f'<Conversation {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'job_posting_id': self.job_posting_id,
            'subject': self.subject,
            'is_archived_by_user': self.is_archived_by_user,
            'is_archived_by_company': self.is_archived_by_company,
            'last_message_at': self.last_message_at.isoformat() if self.last_message_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RecruitingEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # "career_day", "open_day", "webinar", "interview_day"
    location = db.Column(db.String(100), nullable=True)
    is_virtual = db.Column(db.Boolean, default=False)
    virtual_link = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    max_participants = db.Column(db.Integer, nullable=True)
    registration_deadline = db.Column(db.DateTime, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Relazioni
    event_registrations = db.relationship('EventRegistration', backref='recruiting_event', lazy=True)
    
    def __repr__(self):
        return f'<RecruitingEvent {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'event_type': self.event_type,
            'location': self.location,
            'is_virtual': self.is_virtual,
            'virtual_link': self.virtual_link,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'max_participants': self.max_participants,
            'registration_deadline': self.registration_deadline.isoformat() if self.registration_deadline else None,
            'is_published': self.is_published,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('recruiting_event.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="registered")  # "registered", "confirmed", "attended", "cancelled"
    registration_date = db.Column(db.DateTime, server_default=db.func.now())
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<EventRegistration {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'event_id': self.event_id,
            'user_id': self.user_id,
            'status': self.status,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'notes': self.notes
        }

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="EUR")
    status = db.Column(db.String(50), nullable=False)  # "pending", "paid", "cancelled"
    payment_method = db.Column(db.String(50), nullable=True)
    payment_date = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.Text, nullable=False)
    billing_address = db.Column(db.Text, nullable=False)
    tax_id = db.Column(db.String(50), nullable=True)
    vat_rate = db.Column(db.Numeric(5, 2), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<Invoice {self.invoice_number}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'invoice_number': self.invoice_number,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'description': self.description,
            'billing_address': self.billing_address,
            'tax_id': self.tax_id,
            'vat_rate': float(self.vat_rate) if self.vat_rate else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
