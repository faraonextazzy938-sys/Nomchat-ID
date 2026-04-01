const API = '/api';
let currentUser = null;
let selectedAvatar = null;

document.addEventListener('DOMContentLoaded', async () => {
    const res = await fetch(`${API}/auth/me`, { credentials:'include' });
    if (!res.ok) { window.location.href = 'login.html'; return; }
    currentUser = await res.json();

    // Заполняем профиль
    document.getElementById('profile-username').textContent = currentUser.username;
    document.getElementById('profile-email').textContent    = currentUser.email;
    document.getElementById('profile-avatar').innerHTML     = getAvatarHTML(currentUser.avatar || 'skull', '3em');
    document.getElementById('acc-email').textContent        = currentUser.email;
    document.getElementById('acc-since').textContent        = fmtDate(currentUser.created_at);
    document.getElementById('acc-login').textContent        = fmtDate(currentUser.last_login);

    // Грид аватаров
    buildAvatarGrid('profile-av-grid', currentUser.avatar || 'skull', onAvatarSelect);
});

function onAvatarSelect(id, el) {
    document.querySelectorAll('#profile-av-grid .av-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');
    selectedAvatar = id;
    document.getElementById('btn-save-av').disabled = false;
}

async function saveAvatar() {
    if (!selectedAvatar) return;
    await fetch(`/api/users/${currentUser.id}/avatar`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ avatar: selectedAvatar })
    });
    document.getElementById('profile-avatar').innerHTML = getAvatarHTML(selectedAvatar, '3em');
    document.getElementById('btn-save-av').disabled = true;
    currentUser.avatar = selectedAvatar;
}

function editUsername() {
    const name = prompt('Enter new username:', currentUser.username);
    if (!name || name.trim() === currentUser.username) return;
    fetch(`/api/users/${currentUser.id}/username`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ username: name.trim() })
    }).then(r => r.json()).then(u => {
        currentUser.username = u.username;
        document.getElementById('profile-username').textContent = u.username;
    });
}

async function logout() {
    await fetch(`${API}/auth/logout`, { method:'POST', credentials:'include' });
    window.location.href = 'login.html';
}

async function deleteAccount() {
    if (!confirm('Are you sure? This cannot be undone.')) return;
    await fetch(`/api/users/${currentUser.id}`, { method:'DELETE', credentials:'include' });
    window.location.href = 'index.html';
}

function fmtDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleDateString('en-US', { day:'numeric', month:'long', year:'numeric' });
}
