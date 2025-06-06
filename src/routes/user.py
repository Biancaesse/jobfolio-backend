from flask import Blueprint, jsonify, request
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    result = []
    for user in users:
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name
        }
        result.append(user_data)
    return jsonify(result)

@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    user_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'bio': user.bio,
        'profile_picture': user.profile_picture
    }
    return jsonify(user_data)

@user_bp.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    # Validazione base
    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Dati mancanti'}), 400
    
    # Verifica se l'utente esiste già
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username già in uso'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email già in uso'}), 400
    
    # Creazione nuovo utente
    new_user = User(
        username=data['username'],
        email=data['email'],
        password=data['password'],  # In produzione, usare password hashate
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        bio=data.get('bio')
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        'id': new_user.id,
        'username': new_user.username,
        'email': new_user.email
    }), 201
