from flask import Blueprint, jsonify, request
from src.models.company.company import Company, CompanyUser, db
import json
from datetime import datetime
import re
import secrets
import string

company_bp = Blueprint('company', __name__)

# Funzione di utilità per generare uno slug
def generate_slug(name):
    # Converti in minuscolo e rimuovi caratteri speciali
    slug = re.sub(r'[^\w\s-]', '', name.lower())
    # Sostituisci spazi con trattini
    slug = re.sub(r'\s+', '-', slug)
    # Aggiungi un suffisso casuale per garantire unicità
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{slug}-{random_suffix}"

# Endpoint per ottenere tutte le aziende
@company_bp.route('/companies', methods=['GET'])
def get_companies():
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    industry = request.args.get('industry')
    size = request.args.get('size')
    is_verified = request.args.get('is_verified', type=bool)
    is_featured = request.args.get('is_featured', type=bool)
    
    # Costruisci la query base
    query = Company.query
    
    # Applica i filtri se presenti
    if industry:
        query = query.filter(Company.industry == industry)
    if size:
        query = query.filter(Company.size == size)
    if is_verified is not None:
        query = query.filter(Company.is_verified == is_verified)
    if is_featured is not None:
        query = query.filter(Company.is_featured == is_featured)
    
    # Esegui la query paginata
    companies_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'companies': [company.to_dict() for company in companies_paginated.items],
        'total': companies_paginated.total,
        'pages': companies_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere una singola azienda
@company_bp.route('/companies/<int:company_id>', methods=['GET'])
def get_company(company_id):
    company = Company.query.get_or_404(company_id)
    return jsonify(company.to_dict())

# Endpoint per ottenere un'azienda tramite slug
@company_bp.route('/companies/slug/<string:slug>', methods=['GET'])
def get_company_by_slug(slug):
    company = Company.query.filter_by(slug=slug).first_or_404()
    return jsonify(company.to_dict())

# Endpoint per creare una nuova azienda
@company_bp.route('/companies', methods=['POST'])
def create_company():
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('name') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica se l'azienda esiste già
    if Company.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email già in uso'}), 400
    
    # Genera lo slug
    slug = generate_slug(data['name'])
    
    # Creazione nuova azienda
    new_company = Company(
        name=data['name'],
        slug=slug,
        email=data['email'],
        password=data['password'],  # In produzione, usare password hashate
        website=data.get('website'),
        industry=data.get('industry'),
        size=data.get('size'),
        founded_year=data.get('founded_year'),
        description=data.get('description'),
        headquarters=data.get('headquarters')
    )
    
    db.session.add(new_company)
    db.session.commit()
    
    # Creazione dell'utente admin per l'azienda
    admin_user = CompanyUser(
        company_id=new_company.id,
        email=data['email'],
        password=data['password'],  # In produzione, usare password hashate
        first_name=data.get('first_name', 'Admin'),
        last_name=data.get('last_name', 'User'),
        role='admin'
    )
    
    db.session.add(admin_user)
    db.session.commit()
    
    return jsonify(new_company.to_dict()), 201

# Endpoint per aggiornare un'azienda
@company_bp.route('/companies/<int:company_id>', methods=['PUT'])
def update_company(company_id):
    company = Company.query.get_or_404(company_id)
    data = request.get_json()
    
    # Aggiorna i campi dell'azienda
    if 'name' in data:
        company.name = data['name']
    if 'email' in data:
        company.email = data['email']
    if 'website' in data:
        company.website = data['website']
    if 'industry' in data:
        company.industry = data['industry']
    if 'size' in data:
        company.size = data['size']
    if 'founded_year' in data:
        company.founded_year = data['founded_year']
    if 'description' in data:
        company.description = data['description']
    if 'mission' in data:
        company.mission = data['mission']
    if 'culture' in data:
        company.culture = data['culture']
    if 'benefits' in data:
        company.benefits = data['benefits']
    if 'headquarters' in data:
        company.headquarters = data['headquarters']
    if 'locations' in data:
        company.locations = json.dumps(data['locations'])
    if 'social_linkedin' in data:
        company.social_linkedin = data['social_linkedin']
    if 'social_twitter' in data:
        company.social_twitter = data['social_twitter']
    if 'social_facebook' in data:
        company.social_facebook = data['social_facebook']
    if 'social_instagram' in data:
        company.social_instagram = data['social_instagram']
    if 'is_featured' in data:
        company.is_featured = data['is_featured']
    
    company.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(company.to_dict())

# Endpoint per eliminare un'azienda
@company_bp.route('/companies/<int:company_id>', methods=['DELETE'])
def delete_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    # In un'applicazione reale, potrebbe essere meglio "soft delete" o archiviare
    db.session.delete(company)
    db.session.commit()
    
    return jsonify({'message': 'Azienda eliminata con successo'})

# Endpoint per verificare un'azienda
@company_bp.route('/companies/<int:company_id>/verify', methods=['PUT'])
def verify_company(company_id):
    company = Company.query.get_or_404(company_id)
    
    company.is_verified = True
    company.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Azienda verificata con successo', 'company': company.to_dict()})

# Endpoint per aggiornare il logo di un'azienda
@company_bp.route('/companies/<int:company_id>/logo', methods=['PUT'])
def update_company_logo(company_id):
    company = Company.query.get_or_404(company_id)
    
    # In un'applicazione reale, qui gestiremmo l'upload del file
    # Per ora, assumiamo che il percorso del logo sia passato nel corpo della richiesta
    data = request.get_json()
    
    if not data or 'logo' not in data:
        return jsonify({'error': 'Percorso del logo mancante'}), 400
    
    company.logo = data['logo']
    company.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Logo aggiornato con successo', 'company': company.to_dict()})

# Endpoint per ottenere le statistiche di un'azienda
@company_bp.route('/companies/<int:company_id>/stats', methods=['GET'])
def get_company_stats(company_id):
    company = Company.query.get_or_404(company_id)
    
    # In un'applicazione reale, qui calcoleremo le statistiche effettive
    # Per ora, restituiamo dati di esempio
    stats = {
        'job_postings_count': len(company.job_postings),
        'active_job_postings_count': sum(1 for jp in company.job_postings if jp.is_published and (jp.expiry_date is None or jp.expiry_date > datetime.utcnow())),
        'total_applications_count': sum(len(jp.applications) for jp in company.job_postings),
        'total_views_count': sum(jp.views_count for jp in company.job_postings),
        'average_applications_per_posting': sum(len(jp.applications) for jp in company.job_postings) / len(company.job_postings) if company.job_postings else 0
    }
    
    return jsonify(stats)
