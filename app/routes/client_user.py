from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
import uuid
import jwt
import datetime
from config import JWT_SECRET

client_routes = Blueprint('client_routes', __name__)

@client_routes.route('/client/signup', methods=['POST'])
def signup():
    data = request.json
    email = data['email']
    password = data['password']
    token = str(uuid.uuid4())

    cursor = current_app.cursor
    cursor.execute("INSERT INTO users (email, password_hash, role, verification_token) VALUES (%s, %s, 'CLIENT', %s)", 
                   (email, password, token))
    current_app.db.commit()

    verify_link = f"http://localhost:5000/client/verify-email/{token}"
    return jsonify({'message': 'Signup successful. Check email to verify.', 'verify_link': verify_link})

@client_routes.route('/client/verify-email/<token>', methods=['GET'])
def verify_email(token):
    cursor = current_app.cursor
    cursor.execute("SELECT * FROM users WHERE verification_token=%s", (token,))
    user = cursor.fetchone()

    if user:
        cursor.execute("UPDATE users SET is_verified=1 WHERE id=%s", (user['id'],))
        current_app.db.commit()
        return jsonify({'message': 'Email verified successfully'})
    return jsonify({'error': 'Invalid token'}), 400

@client_routes.route('/client/login', methods=['POST'])
def client_login():
    data = request.json
    email = data['email']
    password = data['password']

    cursor = current_app.cursor
    cursor.execute("SELECT * FROM users WHERE email=%s AND role='CLIENT'", (email,))
    user = cursor.fetchone()

    if user and password == user['password_hash'] and user['is_verified']:
        token = create_access_token(identity=user['id'])
        return jsonify({'token': token})
    return jsonify({'error': 'Invalid credentials or email not verified'}), 401

@client_routes.route('/client/list-files', methods=['GET'])
@jwt_required()
def list_files():
    cursor = current_app.cursor
    cursor.execute("SELECT id, filename, uploaded_at FROM files")
    files = cursor.fetchall()
    return jsonify({'files': files})

@client_routes.route('/client/download-file/<int:file_id>', methods=['GET'])
@jwt_required()
def get_download_link(file_id):
    token = jwt.encode({"file_id": file_id, "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=10)}, 
                       JWT_SECRET, algorithm="HS256")
    download_link = f"http://localhost:5000/client/secure-download/{token}"
    return jsonify({'download-link': download_link})

@client_routes.route('/client/secure-download/<token>', methods=['GET'])
@jwt_required()
def download_file(token):
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        file_id = data['file_id']
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Link expired'}), 403
    except:
        return jsonify({'error': 'Invalid token'}), 400

    cursor = current_app.cursor
    cursor.execute("SELECT stored_filename FROM files WHERE id=%s", (file_id,))
    file = cursor.fetchone()
    if file:
        return jsonify({'message': 'File is ready', 'file_path': f"/uploads/{file['stored_filename']}"})
    return jsonify({'error': 'File not found'}), 404
