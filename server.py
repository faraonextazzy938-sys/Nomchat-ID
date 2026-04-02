from flask import Flask, request, jsonify, session, send_from_directory, abort
from flask_cors import CORS
from database import db, User, VerificationCode
from email_service import send_code
from datetime import datetime, timedelta
from functools import wraps
import secrets, os, re

app = Flask(__name__, static_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE']   = os.environ.get('RAILWAY_ENVIRONMENT') == 'production'
CORS(app, supports_credentials=True, origins=os.environ.get('ALLOWED_ORIGINS', '*').split(','))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nomchat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Rate limiting (простой in-memory)
_rate = {}
def rate_limit(key, max_calls=5, window=60):
    now = datetime.utcnow().timestamp()
    calls = [t for t in _rate.get(key, []) if now - t < window]
    if len(calls) >= max_calls:
        return False
    calls.append(now)
    _rate[key] = calls
    return True

with app.app_context():
    db.create_all()
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@nomchat.id')
    if not User.query.filter_by(is_admin=True).first():
        db.session.add(User(email=admin_email, username='Admin', is_admin=True))
        db.session.commit()
        print(f'[NOMCHAT] Admin created: {admin_email}')

# ── Decorators ────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid = session.get('user_id')
        if not uid: return jsonify({'error': 'Unauthorized'}), 401
        user = User.query.get(uid)
        if not user: session.clear(); return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, user=user, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        uid = session.get('user_id')
        if not uid: return jsonify({'error': 'Unauthorized'}), 401
        user = User.query.get(uid)
        if not user or not user.is_admin: return jsonify({'error': 'Forbidden'}), 403
        return f(*args, admin=user, **kwargs)
    return decorated

# ── Static ────────────────────────────────────────────────────

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ── Auth API ──────────────────────────────────────────────────

@app.route('/api/auth/send-code', methods=['POST'])
def api_send_code():
    ip = request.remote_addr
    if not rate_limit(f'send:{ip}', max_calls=5, window=300):
        return jsonify({'error': 'Too many requests. Try again later.'}), 429

    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()

    if not email or not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        return jsonify({'error': 'Invalid email'}), 400

    code    = str(secrets.randbelow(900000) + 100000)
    expires = datetime.utcnow() + timedelta(minutes=10)

    VerificationCode.query.filter_by(email=email).delete()
    db.session.add(VerificationCode(email=email, code=code, expires_at=expires))
    db.session.commit()

    sent = send_code(email, code)
    return jsonify({
        'success':   True,
        'demo_code': None if sent else code,
        'message':   'Code sent' if sent else 'Demo mode'
    })

@app.route('/api/auth/verify', methods=['POST'])
def api_verify():
    ip = request.remote_addr
    if not rate_limit(f'verify:{ip}', max_calls=10, window=300):
        return jsonify({'error': 'Too many attempts. Try again later.'}), 429

    data  = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    code  = data.get('code', '').replace(' ', '').strip()

    if not email or not code or len(code) != 6:
        return jsonify({'error': 'Invalid request'}), 400

    vc = VerificationCode.query.filter_by(email=email, code=code).first()
    if not vc:
        return jsonify({'error': 'Invalid code'}), 400
    if vc.expires_at < datetime.utcnow():
        db.session.delete(vc); db.session.commit()
        return jsonify({'error': 'Code expired'}), 400

    db.session.delete(vc)
    user = User.query.filter_by(email=email).first()
    is_new = user is None
    if not user:
        user = User(email=email, username=email.split('@')[0])
        db.session.add(user)
    user.last_login = datetime.utcnow()
    db.session.commit()

    session.clear()
    session['user_id'] = user.id
    session.permanent = True
    return jsonify({'success': True, 'user': user.to_dict(), 'is_new_user': is_new})

@app.route('/api/auth/me')
@login_required
def api_me(user):
    return jsonify(user.to_dict())

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# ── User API ──────────────────────────────────────────────────

@app.route('/api/users/<int:uid>/avatar', methods=['POST'])
@login_required
def update_avatar(uid, user):
    if user.id != uid: return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json(silent=True) or {}
    user.avatar = data.get('avatar', 'skull')[:50]
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/users/<int:uid>/username', methods=['POST'])
@login_required
def update_username(uid, user):
    if user.id != uid: return jsonify({'error': 'Forbidden'}), 403
    data = request.get_json(silent=True) or {}
    name = data.get('username', '').strip()[:50]
    if not name: return jsonify({'error': 'Invalid username'}), 400
    user.username = name
    db.session.commit()
    return jsonify(user.to_dict())

@app.route('/api/users/<int:uid>', methods=['DELETE'])
@login_required
def delete_account(uid, user):
    if user.id != uid: return jsonify({'error': 'Forbidden'}), 403
    db.session.delete(user); db.session.commit()
    session.clear()
    return jsonify({'success': True})

# ── Admin API ─────────────────────────────────────────────────

@app.route('/api/admin/stats')
@admin_required
def admin_stats(admin):
    return jsonify({
        'users': User.query.count(),
        'admins': User.query.filter_by(is_admin=True).count(),
    })

@app.route('/api/admin/users')
@admin_required
def admin_users(admin):
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users])

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
@admin_required
def admin_delete_user(uid, admin):
    u = User.query.get_or_404(uid)
    if u.id == admin.id: return jsonify({'error': 'Cannot delete yourself'}), 400
    db.session.delete(u); db.session.commit()
    return jsonify({'success': True})

@app.route('/api/admin/users/<int:uid>/toggle-admin', methods=['POST'])
@admin_required
def admin_toggle(uid, admin):
    u = User.query.get_or_404(uid)
    if u.id == admin.id: return jsonify({'error': 'Cannot change own role'}), 400
    u.is_admin = not u.is_admin
    db.session.commit()
    return jsonify(u.to_dict())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port)
