/* ============================================
   NOTIFICATIONS PAGE JS
   ============================================ */

const MAX_NOTIFICATIONS = 7;

let notifications = [
    { id: 1, type: "shift", title: "Shift Reminder",          message: "You have a shift tomorrow (Tuesday, June 3) from 9am-1pm", time: "2 hours ago", read: false },
    { id: 2, type: "alert", title: "Urgent: Volunteers Needed", message: "We need 2 more volunteers for Friday. Can you join us?",  time: "2 days ago",  read: true  },
    { id: 3, type: "shift", title: "Shift Approved",           message: "Your availability for this week has been approved",        time: "3 days ago",  read: true  },
    { id: 4, type: "alert", title: "New Shift Available",      message: "A new shift opened up for next Monday. Claim it now!",     time: "5 days ago",  read: false }
];

let nextNotificationId = 5;

document.addEventListener('DOMContentLoaded', function () {
    renderNotifications();
});

function getIcon(type) {
    switch (type) {
        case "shift":  return `<div class="icon-shift"><i class="bi bi-calendar-event"></i></div>`;
        case "alert":  return `<div class="icon-alert"><i class="bi bi-exclamation-circle"></i></div>`;
        default:       return `<div class="icon-check"><i class="bi bi-check-circle"></i></div>`;
    }
}

function renderNotifications() {
    const container  = document.getElementById('notificationsList');
    const emptyState = document.getElementById('emptyState');

    if (notifications.length === 0) {
        container.classList.add('d-none');
        emptyState.classList.remove('d-none');
        return;
    }

    container.classList.remove('d-none');
    emptyState.classList.add('d-none');
    container.innerHTML = '';

    notifications.slice(0, MAX_NOTIFICATIONS).forEach(n => {
        const card = document.createElement('div');
        card.className = `notification-card p-4 ${n.read ? 'notification-read' : ''}`;
        card.onclick = () => markAsRead(n.id);
        card.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="flex-shrink-0">${getIcon(n.type)}</div>
                <div class="ms-3 flex-grow-1">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h5 class="font-serif mb-1 ${n.read ? 'text-muted' : ''}">${n.title}</h5>
                            <p class="mb-1 ${n.read ? 'text-muted' : ''}">${n.message}</p>
                        </div>
                        ${!n.read ? '<span class="unread-dot ms-2 mt-2"></span>' : ''}
                    </div>
                    <p class="time-text mb-0 mt-2">
                        <i class="bi bi-clock me-1"></i>${n.time}
                    </p>
                </div>
            </div>`;
        container.appendChild(card);
    });
}

function addNotification(type, title, message) {
    notifications.unshift({
        id: nextNotificationId++, type, title, message, time: "Just now", read: false
    });
    if (notifications.length > MAX_NOTIFICATIONS) notifications.pop();
    renderNotifications();
    showToast(`New notification: ${title}`);
}

function markAsRead(id) {
    const n = notifications.find(n => n.id === id);
    if (n && !n.read) {
        n.read = true;
        renderNotifications();
        showToast(`Marked "${n.title}" as read`);
    }
}

function markAllRead() {
    if (notifications.every(n => n.read)) {
        showToast('All notifications are already read');
        return;
    }
    notifications.forEach(n => n.read = true);
    renderNotifications();
    showToast('All notifications marked as read');
}