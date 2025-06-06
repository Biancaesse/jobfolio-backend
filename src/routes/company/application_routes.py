from flask import Blueprint, jsonify, request
from src.models.company.job_posting import Application, ApplicationActivity, JobPosting, db
from src.models.company.company import CompanyUser
from src.models.user import User
from datetime import datetime
import json

application_bp = Blueprint('application', __name__)

# Endpoint per ottenere tutte le candidature
@application_bp.route('/applications', methods=['GET'])
def get_applications():
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    job_posting_id = request.args.get('job_posting_id', type=int)
    user_id = request.args.get('user_id', type=int)
    status = request.args.get('status')
    is_archived = request.args.get('is_archived', type=bool)
    
    # Costruisci la query base
    query = Application.query
    
    # Applica i filtri se presenti
    if job_posting_id:
        query = query.filter(Application.job_posting_id == job_posting_id)
    if user_id:
        query = query.filter(Application.user_id == user_id)
    if status:
        query = query.filter(Application.status == status)
    if is_archived is not None:
        query = query.filter(Application.is_archived == is_archived)
    
    # Esegui la query paginata
    applications_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'applications': [application.to_dict() for application in applications_paginated.items],
        'total': applications_paginated.total,
        'pages': applications_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere le candidature di un annuncio specifico
@application_bp.route('/job-postings/<int:job_posting_id>/applications', methods=['GET'])
def get_job_posting_applications(job_posting_id):
    # Verifica che l'annuncio esista
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    status = request.args.get('status')
    is_archived = request.args.get('is_archived', type=bool)
    
    # Costruisci la query base
    query = Application.query.filter_by(job_posting_id=job_posting_id)
    
    # Applica i filtri se presenti
    if status:
        query = query.filter(Application.status == status)
    if is_archived is not None:
        query = query.filter(Application.is_archived == is_archived)
    
    # Ordina per data di creazione (più recenti prima)
    query = query.order_by(Application.created_at.desc())
    
    # Esegui la query paginata
    applications_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta con informazioni aggiuntive sui candidati
    applications_with_users = []
    for application in applications_paginated.items:
        app_dict = application.to_dict()
        user = User.query.get(application.user_id)
        if user:
            app_dict['user'] = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_picture': user.profile_picture
            }
        applications_with_users.append(app_dict)
    
    result = {
        'applications': applications_with_users,
        'total': applications_paginated.total,
        'pages': applications_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere le candidature di un utente specifico
@application_bp.route('/users/<int:user_id>/applications', methods=['GET'])
def get_user_applications(user_id):
    # Verifica che l'utente esista
    user = User.query.get_or_404(user_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    status = request.args.get('status')
    is_archived = request.args.get('is_archived', type=bool)
    
    # Costruisci la query base
    query = Application.query.filter_by(user_id=user_id)
    
    # Applica i filtri se presenti
    if status:
        query = query.filter(Application.status == status)
    if is_archived is not None:
        query = query.filter(Application.is_archived == is_archived)
    
    # Ordina per data di creazione (più recenti prima)
    query = query.order_by(Application.created_at.desc())
    
    # Esegui la query paginata
    applications_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta con informazioni aggiuntive sugli annunci
    applications_with_jobs = []
    for application in applications_paginated.items:
        app_dict = application.to_dict()
        job_posting = JobPosting.query.get(application.job_posting_id)
        if job_posting:
            app_dict['job_posting'] = {
                'id': job_posting.id,
                'title': job_posting.title,
                'company_id': job_posting.company_id,
                'location': job_posting.location,
                'is_remote': job_posting.is_remote,
                'job_type': job_posting.job_type
            }
        applications_with_jobs.append(app_dict)
    
    result = {
        'applications': applications_with_jobs,
        'total': applications_paginated.total,
        'pages': applications_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere una singola candidatura
@application_bp.route('/applications/<int:application_id>', methods=['GET'])
def get_application(application_id):
    application = Application.query.get_or_404(application_id)
    
    # Ottieni informazioni aggiuntive
    user = User.query.get(application.user_id)
    job_posting = JobPosting.query.get(application.job_posting_id)
    
    result = application.to_dict()
    
    # Aggiungi informazioni sull'utente
    if user:
        result['user'] = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture
        }
    
    # Aggiungi informazioni sull'annuncio
    if job_posting:
        result['job_posting'] = {
            'id': job_posting.id,
            'title': job_posting.title,
            'company_id': job_posting.company_id,
            'location': job_posting.location,
            'is_remote': job_posting.is_remote,
            'job_type': job_posting.job_type
        }
    
    return jsonify(result)

# Endpoint per creare una nuova candidatura
@application_bp.route('/job-postings/<int:job_posting_id>/applications', methods=['POST'])
def create_application(job_posting_id):
    # Verifica che l'annuncio esista
    job_posting = JobPosting.query.get_or_404(job_posting_id)
    
    # Verifica che l'annuncio sia pubblicato
    if not job_posting.is_published:
        return jsonify({'error': 'Non è possibile candidarsi a un annuncio non pubblicato'}), 400
    
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('user_id'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica che l'utente esista
    user = User.query.get_or_404(data['user_id'])
    
    # Verifica che l'utente non si sia già candidato per questo annuncio
    existing_application = Application.query.filter_by(
        job_posting_id=job_posting_id,
        user_id=data['user_id']
    ).first()
    
    if existing_application:
        return jsonify({'error': 'Hai già inviato una candidatura per questo annuncio'}), 400
    
    # Creazione nuova candidatura
    new_application = Application(
        job_posting_id=job_posting_id,
        user_id=data['user_id'],
        cover_letter=data.get('cover_letter'),
        resume_url=data.get('resume_url'),
        status='pending'
    )
    
    db.session.add(new_application)
    
    # Incrementa il contatore delle candidature nell'annuncio
    job_posting.applications_count += 1
    
    db.session.commit()
    
    # Crea un'attività per la nuova candidatura
    activity = ApplicationActivity(
        application_id=new_application.id,
        activity_type='status_change',
        description='Candidatura ricevuta'
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify(new_application.to_dict()), 201

# Endpoint per aggiornare lo stato di una candidatura
@application_bp.route('/applications/<int:application_id>/status', methods=['PUT'])
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    data = request.get_json()
    
    if not data or 'status' not in data:
        return jsonify({'error': 'Stato mancante'}), 400
    
    # Verifica che lo stato sia valido
    valid_statuses = ['pending', 'reviewed', 'interview', 'rejected', 'offered', 'hired']
    if data['status'] not in valid_statuses:
        return jsonify({'error': f'Stato non valido. Gli stati validi sono: {", ".join(valid_statuses)}'}), 400
    
    old_status = application.status
    application.status = data['status']
    application.updated_at = datetime.utcnow()
    
    # Aggiungi note se presenti
    if 'company_notes' in data:
        application.company_notes = data['company_notes']
    
    db.session.commit()
    
    # Crea un'attività per il cambio di stato
    company_user_id = data.get('company_user_id')
    
    activity = ApplicationActivity(
        application_id=application_id,
        company_user_id=company_user_id,
        activity_type='status_change',
        description=f'Stato cambiato da {old_status} a {data["status"]}'
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return jsonify({'message': 'Stato aggiornato con successo', 'application': application.to_dict()})

# Endpoint per aggiungere un'attività a una candidatura
@application_bp.route('/applications/<int:application_id>/activities', methods=['POST'])
def add_application_activity(application_id):
    application = Application.query.get_or_404(application_id)
    data = request.get_json()
    
    if not data or not data.get('activity_type') or not data.get('description'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica che il tipo di attività sia valido
    valid_activity_types = ['status_change', 'note', 'interview_scheduled', 'feedback']
    if data['activity_type'] not in valid_activity_types:
        return jsonify({'error': f'Tipo di attività non valido. I tipi validi sono: {", ".join(valid_activity_types)}'}), 400
    
    # Creazione nuova attività
    new_activity = ApplicationActivity(
        application_id=application_id,
        company_user_id=data.get('company_user_id'),
        activity_type=data['activity_type'],
        description=data['description'],
        metadata=json.dumps(data.get('metadata', {})) if data.get('metadata') else None
    )
    
    db.session.add(new_activity)
    db.session.commit()
    
    return jsonify(new_activity.to_dict()), 201

# Endpoint per ottenere le attività di una candidatura
@application_bp.route('/applications/<int:application_id>/activities', methods=['GET'])
def get_application_activities(application_id):
    application = Application.query.get_or_404(application_id)
    
    # Ottieni tutte le attività ordinate per data (più recenti prima)
    activities = ApplicationActivity.query.filter_by(application_id=application_id).order_by(ApplicationActivity.created_at.desc()).all()
    
    # Prepara la risposta con informazioni aggiuntive sugli utenti aziendali
    activities_with_users = []
    for activity in activities:
        activity_dict = activity.to_dict()
        if activity.company_user_id:
            company_user = CompanyUser.query.get(activity.company_user_id)
            if company_user:
                activity_dict['company_user'] = {
                    'id': company_user.id,
                    'first_name': company_user.first_name,
                    'last_name': company_user.last_name,
                    'role': company_user.role
                }
        activities_with_users.append(activity_dict)
    
    return jsonify(activities_with_users)

# Endpoint per archiviare una candidatura
@application_bp.route('/applications/<int:application_id>/archive', methods=['PUT'])
def archive_application(application_id):
    application = Application.query.get_or_404(application_id)
    
    application.is_archived = True
    application.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Candidatura archiviata con successo', 'application': application.to_dict()})

# Endpoint per ripristinare una candidatura archiviata
@application_bp.route('/applications/<int:application_id>/unarchive', methods=['PUT'])
def unarchive_application(application_id):
    application = Application.query.get_or_404(application_id)
    
    application.is_archived = False
    application.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify({'message': 'Candidatura ripristinata con successo', 'application': application.to_dict()})
