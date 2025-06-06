from src.models.user import db
from datetime import datetime

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    logo = db.Column(db.String(255), nullable=True)
    website = db.Column(db.String(255), nullable=True)
    industry = db.Column(db.String(100), nullable=True)
    size = db.Column(db.String(50), nullable=True)  # es. "1-10", "11-50", "51-200", "201-500", "501+"
    founded_year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text, nullable=True)
    mission = db.Column(db.Text, nullable=True)
    culture = db.Column(db.Text, nullable=True)
    benefits = db.Column(db.Text, nullable=True)
    headquarters = db.Column(db.String(100), nullable=True)
    locations = db.Column(db.Text, nullable=True)  # JSON array di locations
    social_linkedin = db.Column(db.String(255), nullable=True)
    social_twitter = db.Column(db.String(255), nullable=True)
    social_facebook = db.Column(db.String(255), nullable=True)
    social_instagram = db.Column(db.String(255), nullable=True)
    subscription_plan = db.Column(db.String(50), nullable=True)  # "free", "basic", "professional", "enterprise"
    subscription_start = db.Column(db.DateTime, nullable=True)
    subscription_end = db.Column(db.DateTime, nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    # Relazioni
    job_postings = db.relationship('JobPosting', backref='company', lazy=True)
    company_users = db.relationship('CompanyUser', backref='company', lazy=True)
    company_media = db.relationship('CompanyMedia', backref='company', lazy=True)
    company_reviews = db.relationship('CompanyReview', backref='company', lazy=True)
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'email': self.email,
            'logo': self.logo,
            'website': self.website,
            'industry': self.industry,
            'size': self.size,
            'founded_year': self.founded_year,
            'description': self.description,
            'mission': self.mission,
            'culture': self.culture,
            'benefits': self.benefits,
            'headquarters': self.headquarters,
            'locations': self.locations,
            'social_linkedin': self.social_linkedin,
            'social_twitter': self.social_twitter,
            'social_facebook': self.social_facebook,
            'social_instagram': self.social_instagram,
            'is_verified': self.is_verified,
            'is_featured': self.is_featured,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CompanyUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # "admin", "recruiter", "viewer"
    phone = db.Column(db.String(20), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<CompanyUser {self.email}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'role': self.role,
            'phone': self.phone,
            'profile_picture': self.profile_picture,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CompanyMedia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    media_type = db.Column(db.String(50), nullable=False)  # "image", "video", "document"
    title = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<CompanyMedia {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'media_type': self.media_type,
            'title': self.title,
            'description': self.description,
            'url': self.url,
            'is_featured': self.is_featured,
            'order': self.order,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CompanyReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    pros = db.Column(db.Text, nullable=True)
    cons = db.Column(db.Text, nullable=True)
    employment_status = db.Column(db.String(50), nullable=True)  # "current", "former"
    job_title = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    
    def __repr__(self):
        return f'<CompanyReview {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'rating': self.rating,
            'pros': self.pros,
            'cons': self.cons,
            'employment_status': self.employment_status,
            'job_title': self.job_title,
            'is_verified': self.is_verified,
            'is_anonymous': self.is_anonymous,
            'is_approved': self.is_approved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
