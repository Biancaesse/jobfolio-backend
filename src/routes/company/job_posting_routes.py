from flask import Blueprint, jsonify, request
from src.models.company.job_posting import JobPosting, db
from src.models.company.company import Company
from datetime import datetime
import json
import re
import secrets
import string

job_posting_bp = Blueprint('job_posting', __name__)

# Funzione di utilità per generare uno slug
def generate_slug(title):
    # Converti in minuscolo e rimuovi caratteri speciali
    slug = re.sub(r'[^\w\s-]', '', title.lower())
    # Sostituisci spazi con trattini
    slug = re.sub(r'\s+', '-', slug)
    # Aggiungi un suffisso casuale per garantire unicità
    random_suffix = ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(6))
    return f"{slug}-{random_suffix}"

# Endpoint per ottenere tutti gli annunci di lavoro
@job_posting_bp.route('/job-postings', methods=['GET'])
def get_job_postings():
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    company_id = request.args.get('company_id', type=int)
    location = request.args.get('location')
    job_type = request.args.get('job_type')
    experience_level = request.args.get('experience_level')
    is_remote = request.args.get('is_remote', type=bool)
    is_published = request.args.get('is_published', type=bool)
    is_featured = request.args.get('is_featured', type=bool)
    
    # Costruisci la query base
    query = JobPosting.query
    
    # Applica i filtri se presenti
    if company_id:
        query = query.filter(JobPosting.company_id == company_id)
    if location:
        query = query.filter(JobPosting.location.like(f'%{location}%'))
    if job_type:
        query = query.filter(JobPosting.job_type == job_type)
    if experience_level:
        query = query.filter(JobPosting.experience_level == experience_level)
    if is_remote is not None:
        query = query.filter(JobPosting.is_remote == is_remote)
    if is_published is not None:
        query = query.filter(JobPosting.is_published == is_published)
    if is_featured is not None:
        query = query.filter(JobPosting.is_featured == is_featured)
    
    # Esegui la query paginata
    job_postings_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'job_postings': [job_posting.to_dict() for job_posting in job_postings_paginated.items],
        'total': job_postings_paginated.total,
        'pages': job_postings_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere gli annunci di lavoro di un'azienda specifica
@job_posting_bp.route('/companies/<int:company_id>/job-postings', methods=['GET'])
def get_company_job_postings(company_id):
    # Verifica che l'azienda esista
    company = Company.query.get_or_404(company_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    is_published = request.args.get('is_published', type=bool)
    
    # Costruisci la query base
    query = JobPosting.query.filter_by(company_id=company_id)
    
    # Applica i filtri se presenti
    if is_published is not None:
        query = query.filter(JobPosting.is_published == is_published)
    
    # Esegui la query paginata
    job_postings_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'job_postings': [job_posting.to_dict() for job_posting in job_postings_paginated.items],
        'total': job_postings_paginated.total,
        'pages': job_postings_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere un singolo annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>', methods=['GET'])
def get_job_posting(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    # Incrementa il contatore delle visualizzazioni
    job_posting.views_count += 1
    db.session.commit()
    
    return jsonify(job_posting.to_dict())

# Endpoint per ottenere un annuncio di lavoro tramite slug
@job_posting_bp.route('/job-postings/slug/<string:slug>', methods=['GET'])
def get_job_posting_by_slug(slug):
    job_posting = JobPosting.query.filter_by(slug=slug).first_or_404()
    
    # Incrementa il contatore delle visualizzazioni
    job_posting.views_count += 1
    db.session.commit()
    
    return jsonify(job_posting.to_dict())

# Endpoint per creare un nuovo annuncio di lavoro
@job_posting_bp.route('/companies/<int:company_id>/job-postings', methods=['POST'])
def create_job_posting(company_id):
    # Verifica che l'azienda esista
    company = Company.query.get_or_404(company_id)
    
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('title') or not data.get('description') or not data.get('requirements') or not data.get('responsibilities'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Genera lo slug
    slug = generate_slug(data['title'])
    
    # Creazione nuovo annuncio di lavoro
    new_job_posting = JobPosting(
        company_id=company_id,
        title=data['title'],
        slug=slug,
        description=data['description'],
        requirements=data['requirements'],
        responsibilities=data['responsibilities'],
        location=data.get('location', ''),
        is_remote=data.get('is_remote', False),
        is_hybrid=data.get('is_hybrid', False),
        job_type=data.get('job_type', 'full-time'),
        experience_level=data.get('experience_level', 'mid'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        salary_currency=data.get('salary_currency', 'EUR'),
        salary_period=data.get('salary_period', 'year'),
        benefits=data.get('benefits'),
        skills=json.dumps(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills'),
        application_url=data.get('application_url'),
        application_email=data.get('application_email'),
        application_instructions=data.get('application_instructions'),
        is_published=data.get('is_published', False),
        is_featured=data.get('is_featured', False),
        expiry_date=data.get('expiry_date')
    )
    
    # Se l'annuncio è pubblicato, imposta la data di pubblicazione
    if new_job_posting.is_published:
        new_job_posting.publish_date = datetime.utcnow()
    
    db.session.add(new_job_posting)
    db.session.commit()
    
    return jsonify(new_job_posting.to_dict()), 201

# Endpoint per aggiornare un annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>', methods=['PUT'])
def update_job_posting(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    data = request.get_json()
    
    # Aggiorna i campi dell'annuncio
    if 'title' in data:
        job_posting.title = data['title']
    if 'description' in data:
        job_posting.description = data['description']
    if 'requirements' in data:
        job_posting.requirements = data['requirements']
    if 'responsibilities' in data:
        job_posting.responsibilities = data['responsibilities']
    if 'location' in data:
        job_posting.location = data['location']
    if 'is_remote' in data:
        job_posting.is_remote = data['is_remote']
    if 'is_hybrid' in data:
        job_posting.is_hybrid = data['is_hybrid']
    if 'job_type' in data:
        job_posting.job_type = data['job_type']
    if 'experience_level' in data:
        job_posting.experience_level = data['experience_level']
    if 'salary_min' in data:
        job_posting.salary_min = data['salary_min']
    if 'salary_max' in data:
        job_posting.salary_max = data['salary_max']
    if 'salary_currency' in data:
        job_posting.salary_currency = data['salary_currency']
    if 'salary_period' in data:
        job_posting.salary_period = data['salary_period']
    if 'benefits' in data:
        job_posting.benefits = data['benefits']
    if 'skills' in data:
        job_posting.skills = json.dumps(data['skills']) if isinstance(data['skills'], list) else data['skills']
    if 'application_url' in data:
        job_posting.application_url = data['application_url']
    if 'application_email' in data:
        job_posting.application_email = data['application_email']
    if 'application_instructions' in data:
        job_posting.application_instructions = data['application_instructions']
    if 'is_featured' in data:
        job_posting.is_featured = data['is_featured']
    if 'expiry_date' in data:
        job_posting.expiry_date = data['expiry_date']
    
    job_posting.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(job_posting.to_dict())

# Endpoint per pubblicare un annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>/publish', methods=['PUT'])
def publish_job_posting(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    # Verifica che l'annuncio abbia tutti i campi obbligatori
    if not job_posting.title or not job_posting.description or not job_posting.requirements or not job_posting.responsibilities or not job_posting.location:
        return jsonify({'error': 'Annuncio incompleto. Compila tutti i campi obbligatori prima di pubblicare.'}), 400
    
    # Verifica che ci sia una data di scadenza
    if not job_posting.expiry_date:
        return jsonify({'error': 'Imposta una data di scadenza prima di pubblicare l\'annuncio.'}), 400
    
    job_posting.is_published = True
    job_posting.publish_date = datetime.utcnow()
    job_posting.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Annuncio pubblicato con successo', 'job_posting': job_posting.to_dict()})

# Endpoint per ritirare un annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>/unpublish', methods=['PUT'])
def unpublish_job_posting(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    job_posting.is_published = False
    job_posting.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Annuncio ritirato con successo', 'job_posting': job_posting.to_dict()})

# Endpoint per eliminare un annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>', methods=['DELETE'])
def delete_job_posting(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    db.session.delete(job_posting)
    db.session.commit()
    
    return jsonify({'message': 'Annuncio eliminato con successo'})

# Endpoint per ottenere le statistiche di un annuncio di lavoro
@job_posting_bp.route('/job-postings/<int:job_posting_id>/stats', methods=['GET'])
def get_job_posting_stats(job_posting_id):
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    # Calcola le statistiche
    stats = {
        'views_count': job_posting.views_count,
        'applications_count': job_posting.applications_count,
        'conversion_rate': (job_posting.applications_count / job_posting.views_count * 100) if job_posting.views_count > 0 else 0,
        'days_active': (datetime.utcnow() - job_posting.publish_date).days if job_posting.publish_date else 0,
        'applications_per_day': job_posting.applications_count / max(1, (datetime.utcnow() - job_posting.publish_date).days) if job_posting.publish_date else 0
    }
    
    return jsonify(stats)
