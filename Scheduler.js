/* ============================================
   SCHEDULER PAGE JS
   ============================================ */

let currentDate   = new Date();
let currentMonth  = currentDate.getMonth();
let currentYear   = currentDate.getFullYear();
let selectedDays  = new Set();
let assignedDays  = new Set(); // Store assigned work days (locked)

const monthNames = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
];
const WEEKEND_DAYS = [0, 6];

document.addEventListener('DOMContentLoaded', function () {
    renderCalendar();
    updateAvailabilityDisplay();
});

function renderCalendar() {
    const grid = document.getElementById('calendarGrid');
    const headers = Array.from(grid.children).slice(0, 7);
    grid.innerHTML = '';
    headers.forEach(h => grid.appendChild(h));

    const firstDay        = new Date(currentYear, currentMonth, 1).getDay();
    const daysInMonth     = new Date(currentYear, currentMonth + 1, 0).getDate();
    const daysInPrevMonth = new Date(currentYear, currentMonth, 0).getDate();

    document.getElementById('calendarMonthYear').textContent =
        `${monthNames[currentMonth]} ${currentYear}`;

    // Filler days from previous month
    if (firstDay > 0) {
        for (let i = firstDay - 1; i >= 0; i--) {
            grid.appendChild(createDayElement(daysInPrevMonth - i, true, false));
        }
    }

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    for (let i = 1; i <= daysInMonth; i++) {
        const dateObj   = new Date(currentYear, currentMonth, i);
        const dayOfWeek = dateObj.getDay();
        const isWeekend = WEEKEND_DAYS.includes(dayOfWeek);
        const isPast    = dateObj < today;
        const dateStr   = formatDate(currentYear, currentMonth, i);
        const day       = createDayElement(i, false, isWeekend);

        if (!isWeekend) {
            if (isPast) {
                day.classList.add('past');
            } else {
                // Check if day is assigned (locked)
                if (assignedDays.has(dateStr)) {
                    day.classList.add('assigned');
                    // No click listener for assigned days — they are locked!
                } else {
                    // Normal selectable day
                    if (selectedDays.has(dateStr)) day.classList.add('selected');
                    if (
                        i === today.getDate() &&
                        currentMonth === today.getMonth() &&
                        currentYear === today.getFullYear()
                    ) day.classList.add('today');
                    day.addEventListener('click', () => toggleDay(dateStr, day));
                }
            }
        }
        grid.appendChild(day);
    }

    // Filler days from next month
    const totalCells = grid.children.length - 7;
    const remaining  = 42 - totalCells;
    for (let i = 1; i <= remaining; i++) {
        grid.appendChild(createDayElement(i, true, false));
    }
}

function createDayElement(dayNum, isOtherMonth, isWeekend) {
    const div = document.createElement('div');
    div.className = 'calendar-day';
    if (isOtherMonth) div.classList.add('other-month');
    if (isWeekend) {
        div.classList.add('weekend');
        div.innerHTML = `<span class="closed-label">Closed</span>`;
        div.title = "We are closed on weekends";
    } else {
        div.textContent = dayNum;
    }
    return div;
}

function formatDate(year, month, day) {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function toggleDay(dateStr, element) {
    // Prevent toggling if day is assigned (locked)
    if (assignedDays.has(dateStr)) {
        showToast('This day is already assigned to you and cannot be changed.');
        return;
    }

    if (selectedDays.has(dateStr)) {
        selectedDays.delete(dateStr);
        element.classList.remove('selected');
    } else {
        selectedDays.add(dateStr);
        element.classList.add('selected');
    }
    updateAvailabilityDisplay();
    validateSelection();
}

function updateAvailabilityDisplay() {
    // Count only selected days (not assigned ones)
    document.getElementById('selectedCount').textContent = selectedDays.size;
    updateSubmitButton();
}

function validateSelection() {
    const daysWanted = parseInt(document.getElementById('daysWanted').value) || 0;
    const validationAlert = document.getElementById('validationAlert');
    const validationMessage = document.getElementById('validationMessage');

    if (selectedDays.size > 0 && selectedDays.size < daysWanted) {
        validationAlert.classList.remove('d-none');
        validationMessage.textContent = 
            `You must select at least ${daysWanted} days (your preference). You can select more.`;
        return false;
    } else {
        validationAlert.classList.add('d-none');
        return true;
    }
}

function updateSubmitButton() {
    const daysWanted = parseInt(document.getElementById('daysWanted').value) || 0;
    const submitBtn = document.getElementById('submitBtn');
    
    // Enable only if selected days >= days wanted (can be more)
    submitBtn.disabled = selectedDays.size === 0 || selectedDays.size < daysWanted;
}

// Listen for preference changes
document.getElementById('daysWanted').addEventListener('change', function() {
    updateAvailabilityDisplay();
    validateSelection();
});

function changeMonth(delta) {
    currentMonth += delta;
    if (currentMonth > 11) { currentMonth = 0; currentYear++; }
    else if (currentMonth < 0) { currentMonth = 11; currentYear--; }
    renderCalendar();
}

function clearAllSelections() {
    // Only clear selected days, not assigned ones
    if (selectedDays.size === 0) return;
    if (confirm('Are you sure you want to clear all selected days? Assigned days will remain.')) {
        selectedDays.clear();
        renderCalendar();
        updateAvailabilityDisplay();
        showToast('All selections cleared. Assigned days remain.');
    }
}

function submitSchedule() {
    const daysWanted = document.getElementById('daysWanted').value;
    
    // Validate minimum requirement
    if (!validateSelection()) {
        showToast('Please select at least ' + daysWanted + ' days.');
        return;
    }

    const sorted = Array.from(selectedDays).sort();
    const daysList = sorted.map(dateStr => {
        const [y, m, d] = dateStr.split('-');
        return new Date(y, m - 1, d).toLocaleDateString('en-US', {
            weekday: 'long', month: 'long', day: 'numeric'
        });
    });

    const message =
        `We Share & Care Food Bank\n\n` +
        `Days you want to work: ${daysWanted}\n` +
        `Days you're available: ${selectedDays.size}\n\n` +
        `Your available days:\n${daysList.join('\n')}\n\n` +
        `Submit this availability?`;

    if (confirm(message)) {
        // Simulate assigning days (in real app, this would come from admin)
        // For demo: assign the first 'daysWanted' selected days
        assignWorkDays(sorted, daysWanted);
        
        showToast('Thank you! Your availability has been submitted.');
        console.log('Days wanted:', daysWanted);
        console.log('Available days:', sorted);
    }
}

function assignWorkDays(sortedDays, count) {
    // Assign the first 'count' days (or all if less than count)
    const numToAssign = Math.min(count, sortedDays.length);
    for (let i = 0; i < numToAssign; i++) {
        assignedDays.add(sortedDays[i]);
        // Remove from selected since it's now assigned
        selectedDays.delete(sortedDays[i]);
    }
    
    renderCalendar(); // Re-render to show assigned styling
    updateAvailabilityDisplay();
}