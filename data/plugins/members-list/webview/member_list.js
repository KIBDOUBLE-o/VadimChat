// ---------------------------
// UI слой
// ---------------------------
const MembersUI = {
    gameEl: document.getElementById('membersGame'),
    listEl: document.getElementById('membersList'),
    countEl: document.getElementById('membersCount'),

    show() {
        this.gameEl.style.display = 'flex';
    },

    hide() {
        this.gameEl.style.display = 'none';
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    render(members) {
        this.countEl.textContent = members.length;
        this.listEl.innerHTML = '';

        if (members.length === 0) {
            this.listEl.innerHTML = '<div class="members-empty">Нет участников</div>';
            return;
        }

        // Сортировка: админы первыми, затем по имени
        const sorted = [...members].sort((a, b) => {
            if (a[2] !== b[2]) return a[2] ? -1 : 1;
            return a[0].localeCompare(b[0]);
        });

        sorted.forEach(([name, ip, isAdmin]) => {
            const initials = name
                .split(' ')
                .map(w => w[0])
                .join('')
                .substring(0, 2)
                .toUpperCase();

            const item = document.createElement('div');
            item.className = 'member-item';
            item.innerHTML = `
                <div class="member-avatar ${isAdmin ? 'admin' : 'user'}">
                    ${this.escapeHtml(initials)}
                </div>
                <div class="member-info">
                    <div class="member-name">
                        ${this.escapeHtml(name)}
                        ${isAdmin ? '<span class="admin-badge">Admin</span>' : ''}
                    </div>
                    <div class="member-ip">${this.escapeHtml(ip)}</div>
                </div>
                <div class="member-status"></div>
            `;
            this.listEl.appendChild(item);
        });
    }
};


// ---------------------------
// Данные
// ---------------------------
let currentMembers = [];


// ---------------------------
// API — вызов из Python / извне
// ---------------------------
function updateMembersList(members) {
    currentMembers = members;
    MembersUI.render(currentMembers);
}


// ---------------------------
// Обработчики кнопок
// ---------------------------
document.getElementById('membersBtn').onclick = () => {
    MembersUI.show();
};

document.getElementById('closeMembers').onclick = () => {
    MembersUI.hide();
};