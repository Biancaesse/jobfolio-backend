from flask import Blueprint, jsonify, request
from src.models.company.company import CompanyUser, Company, db
from datetime import datetime

company_user_bp = Blueprint('company_user', __name__)

# Endpoint per ottenere tutti gli utenti di un'azienda
@company_user_bp.route('/companies/<int:company_id>/users', methods=['GET'])
def get_company_users(company_id):
    # Verifica che l'azienda esista
    company = Company.query.get_or_404(company_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    role = request.args.get('role')
    is_active = request.args.get('is_active', type=bool)
    
    # Costruisci la query base
    query = CompanyUser.query.filter_by(company_id=company_id)
    
    # Applica i filtri se presenti
    if role:
        query = query.filter(CompanyUser.role == role)
    if is_active is not None:
        query = query.filter(CompanyUser.is_active == is_active)
    
    # Esegui la query paginata
    users_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'users': [user.to_dict() for user in users_paginated.items],
        'total': users_paginated.total,
        'pages': users_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere un singolo utente aziendale
@company_user_bp.route('/company-users/<int:user_id>', methods=['GET'])
def get_company_user(user_id):
    user = CompanyUser.query.get_or_404(user_id)
    return jsonify(user.to_dict())

# Endpoint per creare un nuovo utente aziendale
@company_user_bp.route('/companies/<int:company_id>/users', methods=['POST'])
def create_company_user(company_id):
    # Verifica che l'azienda esista
    company = Company.query.get_or_404(company_id)
    
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('email') or not data.get('password') or not data.get('first_name') or not data.get('last_name') or not data.get('role'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica se l'utente esiste già
    if CompanyUser.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email già in uso'}), 400
    
    # Verifica che il ruolo sia valido
    valid_roles = ['admin', 'recruiter', 'viewer']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Ruolo non valido. I ruoli validi sono: {", ".join(valid_roles)}'}), 400
    
    # Creazione nuovo utente aziendale
    new_user = CompanyUser(
        company_id=company_id,
        email=data['email'],
        password=data['password'],  # In produzione, usare password hashate
        first_name=data['first_name'],
        last_name=data['last_name'],
        role=data['role'],
        phone=data.get('phone'),
        profile_picture=data.get('profile_picture'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify(new_user.to_dict()), 201

# Endpoint per aggiornare un utente aziendale
@company_user_bp.route('/company-users/<int:user_id>', methods=['PUT'])
def update_company_user(user_id):
    user = CompanyUser.query.get_or_404(user_id)
    data = request.get_json()
    
    # Aggiorna i campi dell'utente
    if 'email' in data:
        # Verifica che l'email non sia già in uso da un altro utente
        existing_user = CompanyUser.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'Email già in uso'}), 400
        user.email = data['email']
    
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']
    if 'role' in data:
        # Verifica che il ruolo sia valido
        valid_roles = ['admin', 'recruiter', 'viewer']
        if data['role'] not in valid_roles:
            return jsonify({'error': f'Ruolo non valido. I ruoli validi sono: {", ".join(valid_roles)}'}), 400
        user.role = data['role']
    if 'phone' in data:
        user.phone = data['phone']
    if 'profile_picture' in data:
        user.profile_picture = data['profile_picture']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'password' in data:
        user.password = data['password']  # In produzione, usare password hashate
    
    user.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return jsonify(user.to_dict())

# Endpoint per eliminare un utente aziendale
@company_user_bp.route('/company-users/<int:user_id>', methods=['DELETE'])
def delete_company_user(user_id):
    user = CompanyUser.query.get_or_404(user_id)
    
    # Verifica che non sia l'ultimo admin dell'azienda
    admin_count = CompanyUser.query.filter_by(company_id=user.company_id, role='admin').count()
    if user.role == 'admin' and admin_count <= 1:
        return jsonify({'error': 'Impossibile eliminare l\'ultimo amministratore dell\'azienda'}), 400
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Utente aziendale eliminato con successo'})

# Endpoint per il login degli utenti aziendali
@company_user_bp.route('/company-users/login', methods=['POST'])
def login_company_user():
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email e password sono obbligatorie'}), 400
    
    user = CompanyUser.query.filter_by(email=data['email']).first()
    
    if not user or user.password != data['password']:  # In produzione, verificare la password hashata
        return jsonify({'error': 'Credenziali non valide'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account disattivato'}), 403
    
    # Aggiorna l'ultimo accesso
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    # In un'applicazione reale, qui genereremmo un token JWT
    return jsonify({
        'message': 'Login effettuato con successo',
        'user': user.to_dict(),
        'company': user.company.to_dict()
    })

# Endpoint per il reset della password
@company_user_bp.route('/company-users/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    
    if not data or not data.get('email'):
        return jsonify({'error': 'Email obbligatoria'}), 400
    
    user = CompanyUser.query.filter_by(email=data['email']).first()
    
    if not user:
        # Per motivi di sicurezza, non rivelare che l'utente non esiste
        return jsonify({'message': 'Se l\'email è associata a un account, riceverai istruzioni per reimpostare la password'}), 200
    
    # In un'applicazione reale, qui genereremmo un token di reset e invieremmo un'email
    # Per ora, simuliamo il processo
    
    return jsonify({'message': 'Se l\'email è associata a un account, riceverai istruzioni per reimpostare la password'}), 200
