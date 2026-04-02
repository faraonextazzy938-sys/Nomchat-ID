const API = '';

const AVATARS = [
    { id:'skull', type:'svg', content:`<svg viewBox="0 0 100 100"><circle cx="50" cy="50" r="48" fill="#000"/><circle cx="50" cy="50" r="42" fill="#f5c400"/><ellipse cx="50" cy="47" rx="20" ry="19" fill="#000"/><ellipse cx="50" cy="47" rx="16" ry="15" fill="#f5c400"/><circle cx="41" cy="45" r="6" fill="#000"/><circle cx="59" cy="45" r="6" fill="#000"/><polygon points="50,55 46,63 54,63" fill="#000"/></svg>` },
    { id:'bolt',   type:'emoji', content:'⚡' },
    { id:'star',   type:'emoji', content:'⭐' },
    { id:'fire',   type:'emoji', content:'🔥' },
    { id:'sword',  type:'emoji', content:'⚔️' },
    { id:'shield', type:'emoji', content:'🛡️' },
    { id:'gem',    type:'emoji', content:'💎' },
    { id:'trophy', type:'emoji', content:'🏆' },
    { id:'skull2', type:'emoji', content:'💀' },
    { id:'robot',  type:'emoji', content:'🤖' },
    { id:'alien',  type:'emoji', content:'👾' },
    { id:'ninja',  type:'emoji', content:'🥷' },
    { id:'dragon', type:'emoji', content:'🐉' },
    { id:'wolf',   type:'emoji', content:'🐺' },
    { id:'lion',   type:'emoji', content:'🦁' },
    { id:'ghost',  type:'emoji', content:'👻' },
    { id:'demon',  type:'emoji', content:'😈' },
    { id:'crown',  type:'emoji', content:'👑' },
    { id:'eagle',  type:'emoji', content:'🦅' },
    { id:'shark',  type:'emoji', content:'🦈' },
];

let state = { email: '', selectedAvatar: null };

document.addEventListener('DOMContentLoaded', async () => {
    // Check existing session → redirect to profile
    try {
        const res = await fetch(`${API}/api/auth/me`, { credentials: 'include' });
        if (res.ok) { window.location.href = 'profile.html'; return; }
    } catch (_) {}

    buildAvatarGrid();

    // Enter key handlers
    document.getElementById('email-inp').addEventListener('keydown', e => { if (e.key === 'Enter') doLogin(); });
    document.getElementById('code-inp').addEventListener('keydown', e => { if (e.key === 'Enter') doVerify(); });

    // Real-time email validation — activate button when valid
    document.getElementById('email-inp').addEventListener('input', e => {
        const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.target.value.trim());
        document.getElementById('btn-login').classList.toggle('active', ok);
    });

    // Real-time code formatting "123 456"
    document.getElementById('code-inp').addEventListener('input', e => {
        let v = e.target.value.replace(/\D/g, '').slice(0, 6);
        e.target.value = v.length > 3 ? v.slice(0, 3) + ' ' + v.slice(3) : v;
        document.getElementById('btn-verify').classList.toggle('active', v.length === 6);
    });
});

function buildAvatarGrid() {
    const grid = document.getElementById('av-grid');
    grid.innerHTML = AVATARS.map(a => {
        const inner = a.type === 'svg'
            ? `<span style="width:44px;height:44px;display:flex">${a.content}</span>`
            : `<span>${a.content}</span>`;
        return `<div class="sc-av-item" data-id="${a.id}" onclick="selectAvatar('${a.id}',this)">${inner}</div>`;
    }).join('');
}

async function doLogin() {
    const email = document.getElementById('email-inp').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setErr('email-inp'); return; }

    const btn = document.getElementById('btn-login');
    btn.disabled = true;
    btn.innerHTML = '<span class="sc-spinner"></span>Sending...';

    try {
        const res = await fetch(`${API}/api/auth/send-code`, {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email })
        });
        const data = await res.json();
        state.email = email;
        document.getElementById('email-show').textContent = email;

        if (data.demo_code) {
            document.getElementById('demo-val').textContent =
                data.demo_code.slice(0, 3) + ' ' + data.demo_code.slice(3);
            document.getElementById('demo-box').style.display = 'flex';
        } else {
            document.getElementById('demo-box').style.display = 'none';
        }
        goStep(2);
    } catch (_) {
        setErr('email-inp');
    }

    btn.disabled = false;
    btn.innerHTML = 'LOG IN';
}

async function doVerify() {
    const raw = document.getElementById('code-inp').value.replace(/\s/g, '');
    if (raw.length !== 6) { setErr('code-inp'); return; }

    const btn = document.getElementById('btn-verify');
    btn.disabled = true;
    btn.innerHTML = '<span class="sc-spinner"></span>Verifying...';

    try {
        const res = await fetch(`${API}/api/auth/verify`, {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: state.email, code: raw })
        });
        const data = await res.json();

        if (res.ok) {
            document.getElementById('done-username').textContent = data.user?.username || 'Player';
            goStep(3);
        } else {
            setErr('code-inp');
            document.getElementById('code-inp').value = '';
            btn.disabled = false;
            btn.innerHTML = 'CONTINUE';
        }
    } catch (_) {
        setErr('code-inp');
        btn.disabled = false;
        btn.innerHTML = 'CONTINUE';
    }
}

async function resend() {
    try {
        const res = await fetch(`${API}/api/auth/send-code`, {
            method: 'POST', credentials: 'include',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email: state.email })
        });
        const data = await res.json();
        if (data.demo_code) {
            document.getElementById('demo-val').textContent =
                data.demo_code.slice(0, 3) + ' ' + data.demo_code.slice(3);
            document.getElementById('demo-box').style.display = 'flex';
        }
    } catch (_) {}
}

function selectAvatar(id, el) {
    document.querySelectorAll('#av-grid .sc-av-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');
    state.selectedAvatar = id;
    const btn = document.getElementById('btn-av');
    btn.disabled = false;
    btn.classList.add('active');
}

function confirmAvatar() {
    const av = AVATARS.find(a => a.id === state.selectedAvatar);
    if (!av) return;
    const inner = av.type === 'svg'
        ? `<span style="width:52px;height:52px;display:flex">${av.content}</span>`
        : av.content;
    document.getElementById('done-av').innerHTML = inner;

    // Save avatar via API
    fetch(`${API}/api/auth/me`, { credentials: 'include' })
        .then(r => r.json())
        .then(user => {
            fetch(`${API}/api/users/${user.id}/avatar`, {
                method: 'POST', credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ avatar: state.selectedAvatar })
            });
            if (user.username) {
                document.getElementById('done-username').textContent = user.username;
            }
        })
        .catch(() => {});

    goStep(4);
}

function goProfile() {
    window.location.href = 'profile.html';
}

function goStep(n) {
    document.querySelectorAll('.sc-panel').forEach(s => s.classList.remove('active'));
    document.getElementById('s' + n).classList.add('active');

    const fill = document.getElementById('prog-fill');
    const l1 = document.getElementById('lbl-1');
    const l2 = document.getElementById('lbl-2');
    const widths = { 1: '30%', 2: '70%', 3: '90%', 4: '100%' };
    fill.style.width = widths[n] || '30%';

    if (n === 1) {
        l1.classList.add('active'); l1.classList.remove('done');
        l2.classList.remove('active', 'done');
    } else if (n === 2) {
        l1.classList.remove('active'); l1.classList.add('done');
        l2.classList.add('active'); l2.classList.remove('done');
    } else {
        l1.classList.remove('active'); l1.classList.add('done');
        l2.classList.remove('active'); l2.classList.add('done');
    }
}

function setErr(id) {
    const el = document.getElementById(id);
    el.classList.remove('error');
    void el.offsetWidth; // reflow to restart animation
    el.classList.add('error');
    setTimeout(() => el.classList.remove('error'), 1500);
}
