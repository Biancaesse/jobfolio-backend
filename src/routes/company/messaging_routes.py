from flask import Blueprint, jsonify, request
from src.models.company.communication import Conversation, Message, db
from src.models.company.company import Company, CompanyUser
from src.models.user import User
from datetime import datetime

messaging_bp = Blueprint('messaging', __name__)

# Endpoint per ottenere tutte le conversazioni di un'azienda
@messaging_bp.route('/companies/<int:company_id>/conversations', methods=['GET'])
def get_company_conversations(company_id):
    # Verifica che l'azienda esista
    company = Company.query.get_or_404(company_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    is_archived = request.args.get('is_archived', type=bool)
    
    # Costruisci la query base
    query = Conversation.query.filter_by(company_id=company_id)
    
    # Applica i filtri se presenti
    if is_archived is not None:
        query = query.filter(Conversation.is_archived_by_company == is_archived)
    
    # Ordina per data dell'ultimo messaggio (più recenti prima)
    query = query.order_by(Conversation.last_message_at.desc())
    
    # Esegui la query paginata
    conversations_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta con informazioni aggiuntive sugli utenti
    conversations_with_users = []
    for conversation in conversations_paginated.items:
        conv_dict = conversation.to_dict()
        
        # Aggiungi informazioni sull'utente
        user = User.query.get(conversation.user_id)
        if user:
            conv_dict['user'] = {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'profile_picture': user.profile_picture
            }
        
        # Aggiungi l'ultimo messaggio
        last_message = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.desc()).first()
        if last_message:
            conv_dict['last_message'] = {
                'id': last_message.id,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender_type': last_message.sender_type,
                'is_read': last_message.is_read,
                'created_at': last_message.created_at.isoformat() if last_message.created_at else None
            }
        
        # Aggiungi il conteggio dei messaggi non letti
        unread_count = Message.query.filter_by(
            conversation_id=conversation.id,
            sender_type='user',
            is_read=False
        ).count()
        conv_dict['unread_count'] = unread_count
        
        conversations_with_users.append(conv_dict)
    
    result = {
        'conversations': conversations_with_users,
        'total': conversations_paginated.total,
        'pages': conversations_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere tutte le conversazioni di un utente
@messaging_bp.route('/users/<int:user_id>/conversations', methods=['GET'])
def get_user_conversations(user_id):
    # Verifica che l'utente esista
    user = User.query.get_or_404(user_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Parametri di filtro
    is_archived = request.args.get('is_archived', type=bool)
    
    # Costruisci la query base
    query = Conversation.query.filter_by(user_id=user_id)
    
    # Applica i filtri se presenti
    if is_archived is not None:
        query = query.filter(Conversation.is_archived_by_user == is_archived)
    
    # Ordina per data dell'ultimo messaggio (più recenti prima)
    query = query.order_by(Conversation.last_message_at.desc())
    
    # Esegui la query paginata
    conversations_paginated = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta con informazioni aggiuntive sulle aziende
    conversations_with_companies = []
    for conversation in conversations_paginated.items:
        conv_dict = conversation.to_dict()
        
        # Aggiungi informazioni sull'azienda
        company = Company.query.get(conversation.company_id)
        if company:
            conv_dict['company'] = {
                'id': company.id,
                'name': company.name,
                'logo': company.logo
            }
        
        # Aggiungi l'ultimo messaggio
        last_message = Message.query.filter_by(conversation_id=conversation.id).order_by(Message.created_at.desc()).first()
        if last_message:
            conv_dict['last_message'] = {
                'id': last_message.id,
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'sender_type': last_message.sender_type,
                'is_read': last_message.is_read,
                'created_at': last_message.created_at.isoformat() if last_message.created_at else None
            }
        
        # Aggiungi il conteggio dei messaggi non letti
        unread_count = Message.query.filter_by(
            conversation_id=conversation.id,
            sender_type='company',
            is_read=False
        ).count()
        conv_dict['unread_count'] = unread_count
        
        conversations_with_companies.append(conv_dict)
    
    result = {
        'conversations': conversations_with_companies,
        'total': conversations_paginated.total,
        'pages': conversations_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per ottenere una singola conversazione
@messaging_bp.route('/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    
    result = conversation.to_dict()
    
    # Aggiungi informazioni sull'utente
    user = User.query.get(conversation.user_id)
    if user:
        result['user'] = {
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'profile_picture': user.profile_picture
        }
    
    # Aggiungi informazioni sull'azienda
    company = Company.query.get(conversation.company_id)
    if company:
        result['company'] = {
            'id': company.id,
            'name': company.name,
            'logo': company.logo
        }
    
    return jsonify(result)

# Endpoint per creare una nuova conversazione
@messaging_bp.route('/conversations', methods=['POST'])
def create_conversation():
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('user_id') or not data.get('company_id'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica che l'utente e l'azienda esistano
    user = User.query.get_or_404(data['user_id'])
    company = Company.query.get_or_404(data['company_id'])
    
    # Verifica se esiste già una conversazione tra questo utente e questa azienda
    existing_conversation = Conversation.query.filter_by(
        user_id=data['user_id'],
        company_id=data['company_id']
    ).first()
    
    if existing_conversation:
        return jsonify({'error': 'Esiste già una conversazione tra questo utente e questa azienda', 'conversation_id': existing_conversation.id}), 400
    
    # Creazione nuova conversazione
    new_conversation = Conversation(
        user_id=data['user_id'],
        company_id=data['company_id'],
        job_posting_id=data.get('job_posting_id'),
        subject=data.get('subject'),
        last_message_at=datetime.utcnow()
    )
    
    db.session.add(new_conversation)
    db.session.commit()
    
    # Se è stato fornito un messaggio iniziale, crealo
    if 'initial_message' in data and data['initial_message']:
        new_message = Message(
            conversation_id=new_conversation.id,
            sender_type=data.get('sender_type', 'user'),
            sender_id=data['user_id'] if data.get('sender_type', 'user') == 'user' else data.get('company_user_id'),
            content=data['initial_message'],
            is_read=False
        )
        
        db.session.add(new_message)
        db.session.commit()
    
    return jsonify(new_conversation.to_dict()), 201

# Endpoint per ottenere i messaggi di una conversazione
@messaging_bp.route('/conversations/<int:conversation_id>/messages', methods=['GET'])
def get_conversation_messages(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    
    # Parametri di paginazione
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    # Ottieni i messaggi ordinati per data (più vecchi prima)
    messages_paginated = Message.query.filter_by(conversation_id=conversation_id).order_by(Message.created_at).paginate(page=page, per_page=per_page, error_out=False)
    
    # Prepara la risposta
    result = {
        'messages': [message.to_dict() for message in messages_paginated.items],
        'total': messages_paginated.total,
        'pages': messages_paginated.pages,
        'current_page': page
    }
    
    return jsonify(result)

# Endpoint per inviare un nuovo messaggio
@messaging_bp.route('/conversations/<int:conversation_id>/messages', methods=['POST'])
def send_message(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('content') or not data.get('sender_type') or not data.get('sender_id'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica che il tipo di mittente sia valido
    if data['sender_type'] not in ['user', 'company']:
        return jsonify({'error': 'Tipo di mittente non valido. I tipi validi sono: user, company'}), 400
    
    # Verifica che il mittente esista
    if data['sender_type'] == 'user':
        sender = User.query.get_or_404(data['sender_id'])
        # Verifica che l'utente sia quello associato alla conversazione
        if sender.id != conversation.user_id:
            return jsonify({'error': 'L\'utente non è associato a questa conversazione'}), 403
    else:  # company
        sender = CompanyUser.query.get_or_404(data['sender_id'])
        # Verifica che l'utente aziendale appartenga all'azienda associata alla conversazione
        if sender.company_id != conversation.company_id:
            return jsonify({'error': 'L\'utente aziendale non appartiene all\'azienda associata a questa conversazione'}), 403
    
    # Creazione nuovo messaggio
    new_message = Message(
        conversation_id=conversation_id,
        sender_type=data['sender_type'],
        sender_id=data['sender_id'],
        content=data['content'],
        is_read=False
    )
    
    db.session.add(new_message)
    
    # Aggiorna la data dell'ultimo messaggio nella conversazione
    conversation.last_message_at = datetime.utcnow()
    
    # Se la conversazione era archiviata, ripristinala
    if data['sender_type'] == 'user' and conversation.is_archived_by_user:
        conversation.is_archived_by_user = False
    elif data['sender_type'] == 'company' and conversation.is_archived_by_company:
        conversation.is_archived_by_company = False
    
    db.session.commit()
    
    return jsonify(new_message.to_dict()), 201

# Endpoint per segnare un messaggio come letto
@messaging_bp.route('/messages/<int:message_id>/read', methods=['PUT'])
def mark_message_as_read(message_id):
    message = Message.query.get_or_404(message_id)
    
    message.is_read = True
    db.session.commit()
    
    return jsonify({'message': 'Messaggio segnato come letto', 'message_id': message_id})

# Endpoint per segnare tutti i messaggi di una conversazione come letti
@messaging_bp.route('/conversations/<int:conversation_id>/read', methods=['PUT'])
def mark_conversation_as_read(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('reader_type'):
        return jsonify({'error': 'Tipo di lettore mancante'}), 400
    
    # Verifica che il tipo di lettore sia valido
    if data['reader_type'] not in ['user', 'company']:
        return jsonify({'error': 'Tipo di lettore non valido. I tipi validi sono: user, company'}), 400
    
    # Segna come letti tutti i messaggi inviati dal tipo opposto
    sender_type = 'company' if data['reader_type'] == 'user' else 'user'
    unread_messages = Message.query.filter_by(
        conversation_id=conversation_id,
        sender_type=sender_type,
        is_read=False
    ).all()
    
    for message in unread_messages:
        message.is_read = True
    
    db.session.commit()
    
    return jsonify({'message': f'{len(unread_messages)} messaggi segnati come letti'})

# Endpoint per archiviare una conversazione
@messaging_bp.route('/conversations/<int:conversation_id>/archive', methods=['PUT'])
def archive_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('archiver_type'):
        return jsonify({'error': 'Tipo di archiviatore mancante'}), 400
    
    # Verifica che il tipo di archiviatore sia valido
    if data['archiver_type'] not in ['user', 'company']:
        return jsonify({'error': 'Tipo di archiviatore non valido. I tipi validi sono: user, company'}), 400
    
    # Archivia la conversazione per il tipo specificato
    if data['archiver_type'] == 'user':
        conversation.is_archived_by_user = True
    else:  # company
        conversation.is_archived_by_company = True
    
    db.session.commit()
    
    return jsonify({'message': 'Conversazione archiviata con successo'})

# Endpoint per ripristinare una conversazione archiviata
@messaging_bp.route('/conversations/<int:conversation_id>/unarchive', methods=['PUT'])
def unarchive_conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('archiver_type'):
        return jsonify({'error': 'Tipo di archiviatore mancante'}), 400
    
    # Verifica che il tipo di archiviatore sia valido
    if data['archiver_type'] not in ['user', 'company']:
        return jsonify({'error': 'Tipo di archiviatore non valido. I tipi validi sono: user, company'}), 400
    
    # Ripristina la conversazione per il tipo specificato
    if data['archiver_type'] == 'user':
        conversation.is_archived_by_user = False
    else:  # company
        conversation.is_archived_by_company = False
    
    db.session.commit()
    
    return jsonify({'message': 'Conversazione ripristinata con successo'})
