const API = '/api';
let state = { email: '', selectedAvatar: null };

document.addEventListener('DOMContentLoaded', async () => {
    const res = await fetch(`${API}/auth/me`, { credentials:'include' });
    if (res.ok) { window.location.href = 'profile.html'; return; }

    buildAvatarGrid('av-grid', null, selectAvatar);

    document.getElementById('email-inp').addEventListener('keydown', e => { if(e.key==='Enter') doLogin(); });
    document.getElementById('code-inp').addEventListener('keydown', e => { if(e.key==='Enter') doVerify(); });
    document.getElementById('email-inp').addEventListener('input', e => {
        const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e.target.value.trim());
        document.getElementById('btn-login').classList.toggle('ready', ok);
    });
    document.getElementById('code-inp').addEventListener('input', e => {
        let v = e.target.value.replace(/\D/g,'').slice(0,6);
        e.target.value = v.length > 3 ? v.slice(0,3)+' '+v.slice(3) : v;
        document.getElementById('btn-verify').classList.toggle('ready', v.length===6);
    });
});

async function doLogin() {
    const email = document.getElementById('email-inp').value.trim();
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) { setErr('email-inp'); return; }
    const btn = document.getElementById('btn-login');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Sending...';
    const res  = await fetch(`${API}/auth/send-code`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email })
    });
    const data = await res.json();
    state.email = email;
    document.getElementById('email-show').textContent = email;
    if (data.demo_code) {
        document.getElementById('demo-val').textContent = data.demo_code.slice(0,3)+' '+data.demo_code.slice(3);
        document.getElementById('demo-box').style.display = 'flex';
    } else {
        document.getElementById('demo-box').style.display = 'none';
    }
    goStep(2);
    btn.disabled = false; btn.innerHTML = 'LOG IN';
}

async function doVerify() {
    const raw = document.getElementById('code-inp').value.replace(/\s/g,'');
    if (raw.length !== 6) { setErr('code-inp'); return; }
    const btn = document.getElementById('btn-verify');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span>Verifying...';
    const res  = await fetch(`${API}/auth/verify`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email: state.email, code: raw })
    });
    const data = await res.json();
    if (res.ok) {
        document.getElementById('done-username').textContent = data.user.username;
        goStep(3);
    } else {
        setErr('code-inp');
        document.getElementById('code-inp').value = '';
        btn.disabled = false; btn.innerHTML = 'CONTINUE';
    }
}

async function resend() {
    const res  = await fetch(`${API}/auth/send-code`, {
        method:'POST', credentials:'include',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ email: state.email })
    });
    const data = await res.json();
    if (data.demo_code) {
        document.getElementById('demo-val').textContent = data.demo_code.slice(0,3)+' '+data.demo_code.slice(3);
        document.getElementById('demo-box').style.display = 'flex';
    }
}

function selectAvatar(id, el) {
    document.querySelectorAll('#av-grid .av-item').forEach(i => i.classList.remove('selected'));
    el.classList.add('selected');
    state.selectedAvatar = id;
    const btn = document.getElementById('btn-av');
    btn.disabled = false; btn.classList.add('ready');
}

function confirmAvatar() {
    const av = AVATARS.find(a => a.id === state.selectedAvatar);
    const inner = av.type === 'svg'
        ? `<span style="width:52px;height:52px;display:flex">${av.content}</span>`
        : av.content;
    document.getElementById('done-av').innerHTML = inner;
    // Сохраняем аватар через API
    fetch(`${API}/auth/me`, { credentials:'include' }).then(r => r.json()).then(user => {
        fetch(`/api/users/${user.id}/avatar`, {
            method:'POST', credentials:'include',
            headers:{'Content-Type':'application/json'},
            body: JSON.stringify({ avatar: state.selectedAvatar })
        });
    });
    goStep(4);
}

function goProfile() { window.location.href = 'profile.html'; }

function goStep(n) {
    document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
    document.getElementById('s'+n).classList.add('active');
    const fill = document.getElementById('prog-fill');
    const l1 = document.getElementById('lbl-1');
    const l2 = document.getElementById('lbl-2');
    const steps = { 1:'30%', 2:'70%', 3:'90%', 4:'100%' };
    fill.style.width = steps[n] || '30%';
    if (n===1) { l1.classList.add('active'); l1.classList.remove('done'); l2.classList.remove('active','done'); }
    else if (n===2) { l1.classList.remove('active'); l1.classList.add('done'); l2.classList.add('active'); }
    else { l2.classList.remove('active'); l2.classList.add('done'); }
}

function setErr(id) {
    const el = document.getElementById(id);
    el.classList.remove('error'); void el.offsetWidth; el.classList.add('error');
    setTimeout(() => el.classList.remove('error'), 1500);
}
