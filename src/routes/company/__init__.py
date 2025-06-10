from flask import Blueprint
from src.routes.company.company_routes import company_bp
from src.routes.company.company_user_routes import company_user_bp
from src.routes.company.job_posting_routes import job_posting_bp
from src.routes.company.application_routes import application_bp
from src.routes.company.messaging_routes import messaging_bp

# Blueprint principale per la sezione aziende
company_section_bp = Blueprint('company_section', __name__, url_prefix='/api')

# Registra tutti i blueprint della sezione aziende
company_section_bp.register_blueprint(company_bp)
company_section_bp.register_blueprint(company_user_bp)
company_section_bp.register_blueprint(job_posting_bp)
company_section_bp.register_blueprint(application_bp)
company_section_bp.register_blueprint(messaging_bp)
