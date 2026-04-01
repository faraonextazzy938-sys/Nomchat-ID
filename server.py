from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from database import db, User, VerificationCode
from email_service import send_code
from datetime import datetime, timedelta
import secrets, os

app = Flask(__name__, static_folder='.')
app.secret_key = secrets.token_hex(32)
CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nomchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(is_admin=True).first():
        admin = User(email='admin@nomchat.id', username='Admin', is_admin=True)
        db.session.add(admin)
        db.session.commit()
        print('Nomchat admin created: admin@nomchat.id')

# ── Static files ──────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ── Auth API ──────────────────────────────────────────────────

@app.route('/api/auth/send-code', methods=['POST'])
def api_send_code():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    if not email or '@' not in email:
        return jsonify({'error': 'Invalid email'}), 400

    code    = str(secrets.randbelow(900000) + 100000)
    expires = datetime.utcnow() + timedelta(minutes=10)

    VerificationCode.query.filter_by(email=email).delete()
    db.session.add(VerificationCode(email=email, code=code, expires_at=expires))
    db.session.commit()

    sent = send_code(email, code)
    return jsonify({
        'success':    True,
        'demo_code':  None if sent else code,
        'message':    'Code sent' if sent else 'Demo mode'
    })

@app.route('/api/auth/verify', methods=['POST'])
def api_verify():
    data  = request.get_json()
    email = data.get('email', '').strip().lower()
    code  = data.get('code', '').replace(' ', '')

    vc = VerificationCode.query.filter_by(email=email, code=code).first()
    if not vc:
        return jsonify({'error': 'Invalid code'}), 400
    if vc.expires_at < datetime.utcnow():
        db.session.delete(vc)
        db.session.commit()
        return jsonify({'error': 'Code expired'}), 400

    db.session.delete(vc)

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)

    user.last_login = datetime.utcnow()
    db.session.commit()

    session['user_id'] = user.id
    return jsonify({'success': True, 'user': user.to_dict()})

@app.route('/api/auth/me')
def api_me():
    uid = session.get('user_id')
    if not uid:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(user.to_dict())

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ── User API ──────────────────────────────────────────────────

@app.route('/api/users/<int:uid>/avatar', methods=['POST'])
def update_avatar(uid):
    uid_session = session.get('user_id')
    if not uid_session or uid_session != uid:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    user = User.query.get_or_404(uid)
    user.avatar = data.get('avatar', 'skull')
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/users/<int:uid>/username', methods=['POST'])
def update_username(uid):
    uid_session = session.get('user_id')
    if not uid_session or uid_session != uid:
        return jsonify({'error': 'Unauthorized'}), 401
    data = request.get_json()
    user = User.query.get_or_404(uid)
    user.username = data.get('username', user.username)[:50]
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/users/<int:uid>', methods=['DELETE'])
def delete_account(uid):
    uid_session = session.get('user_id')
    if not uid_session or uid_session != uid:
        return jsonify({'error': 'Unauthorized'}), 401
    user = User.query.get_or_404(uid)
    db.session.delete(user)
    db.session.commit()
    session.clear()
    return jsonify({'success': True})

# ── Admin API ─────────────────────────────────────────────────

def require_admin():
    uid = session.get('user_id')
    if not uid:
        return None, (jsonify({'error': 'Unauthorized'}), 401)
    user = User.query.get(uid)
    if not user or not user.is_admin:
        return None, (jsonify({'error': 'Forbidden'}), 403)
    return user, None

@app.route('/api/admin/users')
def admin_users():
    user, err = require_admin()
    if err: return err
    return jsonify([u.to_dict() for u in User.query.order_by(User.created_at.desc()).all()])

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
def admin_delete_user(uid):
    user, err = require_admin()
    if err: return err
    u = User.query.get_or_404(uid)
    db.session.delete(u)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/users/<int:uid>/toggle-admin', methods=['POST'])
def admin_toggle(uid):
    user, err = require_admin()
    if err: return err
    u = User.query.get_or_404(uid)
    u.is_admin = not u.is_admin
    db.session.commit()
    return jsonify(u.to_dict())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
