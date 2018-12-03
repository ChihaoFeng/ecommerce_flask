from flaskr.db.db import get_db
from werkzeug.security import generate_password_hash


def get_user_by_username(username):
    cursor = get_db().cursor()
    cursor.execute('select * from user where email = %s or phone = %s', (username, username))
    return cursor.fetchone()


def get_user_id_by_id(id):
    cursor = get_db().cursor()
    cursor.execute('select id from user where id = %s', (id,))
    return cursor.fetchone()


def get_user_id_by_email(email):
    cursor = get_db().cursor()
    cursor.execute('select id from user where email = %s', (email,))
    return cursor.fetchone()


def get_user_id_by_phone(phone):
    cursor = get_db().cursor()
    cursor.execute('select id from user where phone = %s', (phone,))
    return cursor.fetchone()


def add_user(first_name, last_name, email, phone, password):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('insert into user (first_name, last_name, email, phone, password) values (%s, %s, %s, %s, %s)',
                   (first_name, last_name, email, phone, generate_password_hash(password)))
    db.commit()


def set_user_active_by_email(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('update user set status=%s where email=%s', ('active', email))
    db.commit()
