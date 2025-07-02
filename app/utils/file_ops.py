import os
import uuid
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from flask import current_app, send_from_directory
from werkzeug.utils import secure_filename

def save_uploaded_file(file):
    ext = file.filename.rsplit('.', 1)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return None, 'Invalid extension'

    original = secure_filename(file.filename)
    stored = f"{uuid.uuid4()}_{original}"
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], stored)

    file.save(path)
    return stored, None

def serve_file(stored_filename):
    return send_from_directory(
        current_app.config['UPLOAD_FOLDER'],
        stored_filename, as_attachment=True
    )
