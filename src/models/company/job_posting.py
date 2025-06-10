from src.models.user import db
from datetime import datetime

class JobPosting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100), nullable=False)
    is_remote = db.Column(db.Boolean, default=False)
    is_hybrid = db.Column(db.Boolean, default=False)
    job_type = db.Column(db.String(50), nullable=False)  # "full-time", "part-time", "contract", "internship"
    experience_level = db.Column(db.String(50), nullable=False)  # "entry", "mid", "senior", "executive"
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    salary_currency = db.Column(db.String(3), nullable=True)  # "EUR", "USD", ecc.
    salary_period = db.Column(db.String(10), nullable=True)  # "year", "month", "hour"
    benefits = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  # JSON array di skills
    application_url = db.Column(db.String(255), nullable=True)
    application_email = db.Column(db.String(120), nullable=True)
    application_instructions = db.Column(db.Text, nullable=True)
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    publish_date = db.Column(db.DateTime, nullable=True)
    expiry_date = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Relazioni
    applications = db.relationship('Application', backref='job_posting', lazy=True)
    
    def __repr__(self):
        return f'<JobPosting {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'requirements': self.requirements,
            'responsibilities': self.responsibilities,
            'location': self.location,
            'is_remote': self.is_remote,
            'is_hybrid': self.is_hybrid,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_currency': self.salary_currency,
            'salary_period': self.salary_period,
            'benefits': self.benefits,
            'skills': self.skills,
            'application_url': self.application_url,
            'application_email': self.application_email,
            'application_instructions': self.application_instructions,
            'is_published': self.is_published,
            'is_featured': self.is_featured,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'publish_date': self.publish_date.isoformat() if self.publish_date else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_posting.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    resume_url = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="pending")  # "pending", "reviewed", "interview", "rejected", "offered", "hired"
    company_notes = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Integer, nullable=True)  # 1-5
    is_archived = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Relazioni
    application_activities = db.relationship('ApplicationActivity', backref='application', lazy=True)
    
    def __repr__(self):
        return f'<Application {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_posting_id': self.job_posting_id,
            'user_id': self.user_id,
            'cover_letter': self.cover_letter,
            'resume_url': self.resume_url,
            'status': self.status,
            'company_notes': self.company_notes,
            'rating': self.rating,
            'is_archived': self.is_archived,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ApplicationActivity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    company_user_id = db.Column(db.Integer, db.ForeignKey('company_user.id'), nullable=True)
    activity_type = db.Column(db.String(50), nullable=False)  # "status_change", "note", "interview_scheduled", "feedback"
    description = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.Text, nullable=True)  # JSON con dati aggiuntivi
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<ApplicationActivity {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'application_id': self.application_id,
            'company_user_id': self.company_user_id,
            'activity_type': self.activity_type,
            'description': self.description,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
