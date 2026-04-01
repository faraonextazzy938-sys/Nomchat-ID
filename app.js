// Общие аватары для всего сайта
const AVATARS = [
    { id:'skull',   type:'svg', content:`<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="48" fill="#000"/><circle cx="50" cy="50" r="42" fill="#f5c400"/><ellipse cx="50" cy="47" rx="20" ry="19" fill="#000"/><ellipse cx="50" cy="47" rx="16" ry="15" fill="#f5c400"/><circle cx="41" cy="45" r="6" fill="#000"/><circle cx="59" cy="45" r="6" fill="#000"/><polygon points="50,55 46,63 54,63" fill="#000"/><ellipse cx="43" cy="33" rx="8" ry="4.5" fill="#fff" opacity="0.65" transform="rotate(-20,43,33)"/><rect x="33" y="37" width="7" height="2.5" rx="1.2" fill="#000" transform="rotate(-30,36,38)"/><rect x="57" y="35" width="7" height="2.5" rx="1.2" fill="#000" transform="rotate(25,60,36)"/><rect x="38" y="64" width="24" height="7" rx="3.5" fill="#000"/></svg>` },
    { id:'star',    type:'emoji', content:'⭐' },
    { id:'fire',    type:'emoji', content:'🔥' },
    { id:'sword',   type:'emoji', content:'⚔️' },
    { id:'shield',  type:'emoji', content:'🛡️' },
    { id:'gem',     type:'emoji', content:'💎' },
    { id:'trophy',  type:'emoji', content:'🏆' },
    { id:'bolt',    type:'emoji', content:'⚡' },
    { id:'skull2',  type:'emoji', content:'💀' },
    { id:'robot',   type:'emoji', content:'🤖' },
    { id:'alien',   type:'emoji', content:'👾' },
    { id:'ninja',   type:'emoji', content:'🥷' },
    { id:'dragon',  type:'emoji', content:'🐉' },
    { id:'wolf',    type:'emoji', content:'🐺' },
    { id:'bear',    type:'emoji', content:'🐻' },
    { id:'lion',    type:'emoji', content:'🦁' },
    { id:'eagle',   type:'emoji', content:'🦅' },
    { id:'shark',   type:'emoji', content:'🦈' },
    { id:'ghost',   type:'emoji', content:'👻' },
    { id:'demon',   type:'emoji', content:'😈' },
];

function getAvatarHTML(id, size = '2em') {
    const av = AVATARS.find(a => a.id === id) || AVATARS[0];
    if (av.type === 'svg') {
        return `<span style="width:${size};height:${size};display:flex">${av.content}</span>`;
    }
    return `<span style="font-size:${size}">${av.content}</span>`;
}

function buildAvatarGrid(containerId, selectedId, onSelect) {
    const grid = document.getElementById(containerId);
    if (!grid) return;
    grid.innerHTML = AVATARS.map(a => {
        const inner = a.type === 'svg'
            ? `<span style="width:44px;height:44px;display:flex">${a.content}</span>`
            : `<span>${a.content}</span>`;
        const sel = a.id === selectedId ? 'selected' : '';
        return `<div class="av-item ${sel}" data-id="${a.id}" onclick="(${onSelect.toString()})('${a.id}',this)">${inner}</div>`;
    }).join('');
}

// Проверка авторизации
async function checkAuth() {
    const res = await fetch('/api/auth/me', { credentials:'include' });
    if (!res.ok) return null;
    return res.json();
}

// Обновление шапки
async function initHeader() {
    const user = await checkAuth();
    const area = document.getElementById('header-user-area');
    const navProfile = document.getElementById('nav-profile');
    if (user && area) {
        area.innerHTML = `
            <a href="profile.html" style="display:flex;align-items:center;gap:8px;text-decoration:none;color:#fff">
                <div style="width:32px;height:32px;border-radius:50%;background:linear-gradient(135deg,#7b1fa2,#1565c0);display:flex;align-items:center;justify-content:center;font-size:1.1em">
                    ${getAvatarHTML(user.avatar || 'skull', '1.1em')}
                </div>
                <span style="font-size:0.88em;font-weight:600">${user.username}</span>
            </a>
        `;
        if (navProfile) navProfile.style.display = '';
    }
}

document.addEventListener('DOMContentLoaded', initHeader);
