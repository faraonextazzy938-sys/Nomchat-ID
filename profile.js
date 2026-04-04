const API = '';
let currentUser = null;
let selectedAvatar = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const ctrl = new AbortController();
        setTimeout(() => ctrl.abort(), 5000);
        const res = await fetch(`${API}/api/auth/me`, { credentials:'include', signal:ctrl.signal });
        if (!res.ok) { window.location.href = 'login.html'; return; }
        currentUser = await res.json();
    } catch (_) { window.location.href = 'login.html'; return; }

    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent    = currentUser.email;
    document.getElementById('profile-av').innerHTML         = getAvatarHTML(currentUser.avatar || 'bolt', '3em');
    document.getElementById('acc-email').textContent        = currentUser.email;
    document.getElementById('acc-since').textContent        = fmt(currentUser.created_at);
    document.getElementById('acc-login').textContent        = fmt(currentUser.last_login);

    if (currentUser.is_banned) {
        // Show banned notice and block access
        document.getElementById('adm-badge').style.display = 'none';
        document.getElementById('dev-badge').style.display = 'none';
        document.getElementById('creator-badge').style.display = 'none';
        const bannedBadge = document.createElement('span');
        bannedBadge.innerHTML = '🔨 BANNED';
        bannedBadge.style.cssText = 'background:rgba(239,68,68,0.2);color:#ef4444;border:1px solid rgba(239,68,68,0.4);font-size:0.55em;font-weight:900;padding:3px 8px;border-radius:6px;letter-spacing:1px;';
        document.getElementById('profile-username').after(bannedBadge);
        // Show ban reason
        const banInfo = document.createElement('p');
        banInfo.style.cssText = 'color:#ef4444;font-size:0.82em;margin-top:8px;';
        banInfo.textContent = `Banned: ${currentUser.ban_reason || 'Нарушение правил'}`;
        document.querySelector('.nc-profile-email').after(banInfo);
    }

    if (currentUser.is_admin) {
        document.getElementById('admin-panel-btn').style.display = 'block';
        document.getElementById('adm-badge').style.display = 'inline-block';
    }
    if (currentUser.is_dev || currentUser.email === 'nomchat@nom.ru') {
        document.getElementById('dev-badge').style.display = 'inline-block';
        document.getElementById('dev-panel-btn').style.display = 'block';
    }
    if (currentUser.is_creator || currentUser.email === 'creator@nom.ru') {
        document.getElementById('creator-badge').style.display = 'inline-block';
        document.getElementById('creator-panel-btn').style.display = 'block';
    }
    if (currentUser.is_support) {
        document.getElementById('support-badge').style.display = 'inline-block';
        document.getElementById('support-panel-btn').style.display = 'block';
    }
    // DEV badge for nomchat@nom.ru (legacy)
    if (currentUser.email === 'nomchat@nom.ru') {
        document.getElementById('dev-badge').style.display = 'inline-block';
    }

    buildProfileGrid();
});

function buildProfileGrid() {
    const grid = document.getElementById('av-grid');
    grid.innerHTML = AVATARS_LIST.map(a => {
        const inner = a.type === 'svg'
            ? `<span style="width:36px;height:36px;display:flex">${a.content}</span>`
            : `<span>${a.content}</span>`;
        const sel = a.id === (currentUser.avatar || 'bolt') ? 'selected' : '';
        return `<div class="nc-av-item ${sel}" onclick="onAvSelect('${a.id}',this)">${inner}</div>`;
    }).join('');
}

function onAvSelect(id, el) {
    document.querySelectorAll('.nc-av-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');
    selectedAvatar = id;
    document.getElementById('btn-save-av').disabled = false;
}

async function saveAvatar() {
    if (!selectedAvatar) return;
    await fetch(`${API}/api/users/${currentUser.id}/avatar`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ avatar: selectedAvatar })
    });
    document.getElementById('profile-av').innerHTML = getAvatarHTML(selectedAvatar, '3em');
    document.getElementById('btn-save-av').disabled = true;
    currentUser.avatar = selectedAvatar;
}

function editUsername() {
    const name = prompt('New username:', currentUser.username);
    if (!name || name.trim() === currentUser.username) return;
    fetch(`${API}/api/users/${currentUser.id}/username`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ username: name.trim() })
    }).then(r => r.json()).then(u => {
        currentUser.username = u.username;
        document.getElementById('profile-username').textContent = u.username;
    });
}

async function logout() {
    await fetch(`${API}/api/auth/logout`, { method:'POST', credentials:'include' });
    window.location.href = 'index.html';
}

async function deleteAccount() {
    if (!confirm('Delete your Nomchat ID? This cannot be undone.')) return;
    await fetch(`${API}/api/users/${currentUser.id}`, { method:'DELETE', credentials:'include' });
    window.location.href = 'index.html';
}

function fmt(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-US', { day:'numeric', month:'long', year:'numeric' });
}
