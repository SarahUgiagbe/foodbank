/* ============================================
   SCHEDULER PAGE JS
   ============================================ */

let currentDate   = new Date();
let currentMonth  = currentDate.getMonth();
let currentYear   = currentDate.getFullYear();
let selectedDays  = new Set();
let assignedDays  = new Set();

// Daily capacity limits (Mon=1, Tue=2, Wed=3, Thu=4, Fri=5)
const DAY_CAPACITY = {
    1: { max: 6, current: 0 },  // Monday
    2: { max: 8, current: 0 },  // Tuesday
    3: { max: 4, current: 0 },  // Wednesday
    4: { max: 8, current: 0 },  // Thursday
    5: { max: 5, current: 0 }   // Friday
};

// Track which specific dates are at capacity
let fullDays = new Set();

const monthNames = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
];
const WEEKEND_DAYS = [0, 6];

document.addEventListener('DOMContentLoaded', function () {
    initDemoData();
    renderCalendar();
    updateAvailabilityDisplay();
});

function initDemoData() {
    const demoSignups = {
        '2026-06-08': 4,  // Monday - 4/6
        '2026-06-09': 8,  // Tuesday - 8/8 FULL
        '2026-06-10': 2,  // Wednesday - 2/4
        '2026-06-11': 7,  // Thursday - 7/8
        '2026-06-12': 5,  // Friday - 5/5 FULL
    };

    for (const [dateStr, count] of Object.entries(demoSignups)) {
        const dateObj = new Date(dateStr);
        const dayOfWeek = dateObj.getDay();
        if (DAY_CAPACITY[dayOfWeek]) {
            DAY_CAPACITY[dayOfWeek].current += count;
            if (count >= DAY_CAPACITY[dayOfWeek].max) {
                fullDays.add(dateStr);
            }
        }
    }
}

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
        const day       = createDayElement(i, false, isWeekend, dateStr, dayOfWeek);

        if (!isWeekend) {
            if (isPast) {
                day.classList.add('past');
            } else if (assignedDays.has(dateStr)) {
                // ASSIGNED: locked, display only
                day.classList.add('assigned');
            } else if (fullDays.has(dateStr)) {
                // FULL: cannot select, display only
                day.classList.add('full');
                day.title = "This day is full - no spots available";
            } else {
                // AVAILABLE: selectable
                if (selectedDays.has(dateStr)) day.classList.add('selected');
                if (
                    i === today.getDate() &&
                    currentMonth === today.getMonth() &&
                    currentYear === today.getFullYear()
                ) day.classList.add('today');
                day.addEventListener('click', () => toggleDay(dateStr, day));
            }
        }
        grid.appendChild(day);
    }

    const totalCells = grid.children.length - 7;
    const remaining  = 42 - totalCells;
    for (let i = 1; i <= remaining; i++) {
        grid.appendChild(createDayElement(i, true, false));
    }
}

function createDayElement(dayNum, isOtherMonth, isWeekend, dateStr, dayOfWeek) {
    const div = document.createElement('div');
    div.className = 'calendar-day';
    if (isOtherMonth) div.classList.add('other-month');
    if (isWeekend) {
        div.classList.add('weekend');
        div.innerHTML = `<span class="closed-label">Closed</span>`;
        div.title = "We are closed on weekends";
    } else {
        const dayNumSpan = document.createElement('span');
        dayNumSpan.className = 'day-number';
        dayNumSpan.textContent = dayNum;
        div.appendChild(dayNumSpan);

        if (!isOtherMonth && dateStr && dayOfWeek !== undefined) {
            const capacity = getDayCapacity(dateStr, dayOfWeek);
            const capSpan = document.createElement('span');
            capSpan.className = 'day-capacity';
            capSpan.textContent = `${capacity.current}/${capacity.max}`;
            div.appendChild(capSpan);
        }
    }
    return div;
}

function getDayCapacity(dateStr, dayOfWeek) {
    if (DAY_CAPACITY[dayOfWeek]) {
        let extra = 0;
        if (selectedDays.has(dateStr)) extra++;
        return {
            current: DAY_CAPACITY[dayOfWeek].current + extra,
            max: DAY_CAPACITY[dayOfWeek].max
        };
    }
    return { current: 0, max: 0 };
}

function formatDate(year, month, day) {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
}

function toggleDay(dateStr, element) {
    // BLOCK 1: Cannot toggle assigned days
    if (assignedDays.has(dateStr)) {
        showToast('This day is already assigned to you and cannot be changed.');
        return;
    }

    // BLOCK 2: Cannot toggle full days
    if (fullDays.has(dateStr)) {
        showToast('This day is full - no spots available.');
        return;
    }

    // BLOCK 3: Check if selecting this would make it full (prevent overflow)
    const dateObj = new Date(dateStr);
    const dayOfWeek = dateObj.getDay();
    const capacity = getDayCapacity(dateStr, dayOfWeek);
    
    if (!selectedDays.has(dateStr) && capacity.current >= capacity.max) {
        showToast('This day is full - no spots available.');
        fullDays.add(dateStr);
        renderCalendar();
        return;
    }

    // Toggle selection
    if (selectedDays.has(dateStr)) {
        selectedDays.delete(dateStr);
        element.classList.remove('selected');
    } else {
        selectedDays.add(dateStr);
        element.classList.add('selected');
    }
    
    updateAvailabilityDisplay();
    validateSelection();
    renderCalendar();
}

function updateAvailabilityDisplay() {
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
    submitBtn.disabled = selectedDays.size === 0 || selectedDays.size < daysWanted;
}

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
    if (selectedDays.size === 0) return;
    if (confirm('Are you sure you want to clear all selected days? Assigned days will remain.')) {
        selectedDays.clear();
        renderCalendar();
        updateAvailabilityDisplay();
        showToast('All selections cleared. Assigned days remain.');
    }
}

function submitSchedule() {
    const daysWanted = parseInt(document.getElementById('daysWanted').value) || 0;
    
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
        assignWorkDays(sorted, daysWanted);
        showToast('Thank you! Your availability has been submitted.');
    }
}

function assignWorkDays(sortedDays, count) {
    const numToAssign = Math.min(count, sortedDays.length);
    for (let i = 0; i < numToAssign; i++) {
        assignedDays.add(sortedDays[i]);
        selectedDays.delete(sortedDays[i]);
        
        const dateObj = new Date(sortedDays[i]);
        const dayOfWeek = dateObj.getDay();
        if (DAY_CAPACITY[dayOfWeek]) {
            DAY_CAPACITY[dayOfWeek].current++;
            if (DAY_CAPACITY[dayOfWeek].current >= DAY_CAPACITY[dayOfWeek].max) {
                fullDays.add(sortedDays[i]);
            }
        }
    }
    
    renderCalendar();
    updateAvailabilityDisplay();
}