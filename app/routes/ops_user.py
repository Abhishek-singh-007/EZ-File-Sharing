from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import uuid

from werkzeug.utils import secure_filename
from config import ALLOWED_EXTENSIONS

ops_routes = Blueprint('ops_routes', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ops_routes.route('/ops/login', methods=['POST'])
def ops_login():
    data = request.json
    email = data['email']
    password = data['password']

    cursor = current_app.cursor
    cursor.execute("SELECT * FROM users WHERE email=%s AND role='OPS'", (email,))
    user = cursor.fetchone()

    if user and password == user['password_hash']:  # plain match (later use bcrypt)
        return jsonify({'message': 'Login success', 'user_id': user['id']})
    return jsonify({'error': 'Invalid credentials'}), 401

@ops_routes.route('/ops/upload', methods=['POST'])
@jwt_required()
def upload_file():
    file = request.files['file']
    user_id = get_jwt_identity()

    if not file or not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = secure_filename(file.filename)
    stored_filename = f"{uuid.uuid4()}_{filename}"
    file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], stored_filename))

    cursor = current_app.cursor
    cursor.execute("INSERT INTO files (filename, stored_filename, uploader_id) VALUES (%s, %s, %s)", 
                   (filename, stored_filename, user_id))
    current_app.db.commit()

    return jsonify({'message': 'File uploaded successfully'})
