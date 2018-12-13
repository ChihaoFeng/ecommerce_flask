from flask import Blueprint, request, session, current_app, url_for
from flaskr import dao, mail
from werkzeug.security import check_password_hash
from werkzeug.exceptions import abort
import jwt
import datetime
import json
import facebook
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired

bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        data = request.get_json()
        fname = data.get('first_name', None)
        lname = data.get('last_name', None)
        email = data.get('email', None)
        phone = data.get('phone', None)
        password = data.get('password', None)

        error = None
        if not fname:
            error = 'First name is required.'
        elif not lname:
            error = 'Last name is required.'
        elif not email:
            error = 'Email is required.'
        elif not password:
            error = 'Password is required.'
        elif dao.get_user_id_by_email(email) is not None:
            error = 'Email {} has already registered.'.format(email)
        elif dao.get_user_id_by_phone(phone) is not None:
            error = 'Phone {} has already registered.'.format(phone)

        if error:
            abort(403, error)

        msg = Message('Confirm Email', sender='fengchihao@gamil.com', recipients=[email])
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        token = s.dumps(email, salt='email-confirm')
        link = url_for('.confirm_email', token=token, _external=True)
        msg.body = 'Your link is {}'.format(link)
        mail.send(msg)
        print('email sending...')

        dao.add_user(fname, lname, email, phone, password)
        return 'success'

    return 'Register Page'


@bp.route('/confirm_email/<token>')
def confirm_email(token):
    try:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        email = s.loads(token, salt='email-confirm', max_age=3600)
    except SignatureExpired:
        return abort(401, 'The token is expired')
    # set email to active
    dao.set_user_active_by_email(email)
    return 'Your account is activated!'


def validate(social_media_id, token):
    try:
        graph = facebook.GraphAPI(access_token=token)
        rsp = graph.get_object(id=social_media_id, fields='first_name, last_name, email')
        print('FB said ...', rsp)
    except Exception as e:
        print('FB error = ', e)
        rsp = None
    return rsp


@bp.route('/verifyfb', methods=('GET', 'POST'))
def verify_fb():
    if request.method == 'POST':
        if request.data:
            try:
                dd = request.get_json()
                result = validate(dd['social_id'], dd['social_token'])
            except Exception as e:
                print('Exception e = ', e)
                result = None

            if result is not None:
                user_id = dao.get_user_id_by_email(result['email'])
                if not user_id:
                    dao.add_user(result['first_name'], result['last_name'], result['email'], '', '')
                    user_id = dao.get_user_id_by_email(result['email'])
                id = user_id['id']
                token = jwt.encode(
                    {'public_id': id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                    current_app.config['SECRET_KEY'])
                session.clear()
                session['user_id'] = id
                session['token'] = token
                return json.dumps({'token': token.decode('UTF-8')})
            abort(401)
    return "verifyfb page"


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        data = request.get_json()
        username = data.get('username', None)
        password = data.get('password', None)
        user = dao.get_user_by_username(username)

        error = None
        if not username or user is None or not check_password_hash(user['password'], password):
            error = 'Incorrect username or password.'

        if user['status'] != 'active':
            error = 'Your account is not active.'

        if error is None:
            token = jwt.encode(
                {'public_id': user['id'], 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
                current_app.config['SECRET_KEY'])
            session.clear()
            session['user_id'] = user['id']
            session['token'] = token
            return json.dumps({'token': token.decode("utf-8")})

        abort(401)

    return 'Login Page'


@bp.route('/logout')
def logout():
    print(session)
    session.clear()
    return 'success'


@bp.route('/verifytoken', methods=('GET', 'POST'))
def verify_token():
    if request.method == 'POST':
        data = request.get_json()
        if 'token' not in session:
            return "User has log out"
        if data and 'token' in data:
            token = data['token']
            if token == session['token'].decode("utf-8"):
                return json.dumps({'id': session['user_id']})
        return json.dumps({'id': 'Incorrect token'})
    return 'Verify Token Page'
