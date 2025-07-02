# app/models.py

def get_user_by_email(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    return cursor.fetchone()

def insert_client_user(cursor, email, password, token):
    cursor.execute("""
        INSERT INTO users (email, password_hash, role, verification_token)
        VALUES (%s, %s, 'CLIENT', %s)
    """, (email, password, token))

def mark_user_verified(cursor, user_id):
    cursor.execute("UPDATE users SET is_verified=1 WHERE id=%s", (user_id,))

def get_file_by_id(cursor, file_id):
    cursor.execute("SELECT * FROM files WHERE id=%s", (file_id,))
    return cursor.fetchone()

def insert_uploaded_file(cursor, filename, stored_filename, uploader_id):
    cursor.execute("""
        INSERT INTO files (filename, stored_filename, uploader_id)
        VALUES (%s, %s, %s)
    """, (filename, stored_filename, uploader_id))

def list_all_files(cursor):
    cursor.execute("SELECT id, filename, uploaded_at FROM files")
    return cursor.fetchall()
