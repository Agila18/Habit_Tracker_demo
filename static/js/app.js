/**
 * Habit Tracker Lite - Client JavaScript Application
 * Manages UI interactions, API calls, dynamic card rendering,
 * and user notifications.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements - Header & Stats
    const currentDateText = document.getElementById('current-date-text');
    const statsMotivationText = document.getElementById('stats-motivation-text');
    const percentageBadge = document.getElementById('percentage-badge');
    const progressBarFill = document.getElementById('progress-bar-fill');
    const progressBarWrapper = document.getElementById('progress-bar-wrapper');
    const totalHabitsCount = document.getElementById('total-habits-count');
    const completedHabitsCount = document.getElementById('completed-habits-count');
    const pendingHabitsCount = document.getElementById('pending-habits-count');
    const habitsCounterPill = document.getElementById('habits-counter-pill');

    // DOM Elements - Add Habit Form
    const addHabitForm = document.getElementById('add-habit-form');
    const habitNameInput = document.getElementById('habit-name');
    const habitDescInput = document.getElementById('habit-desc');
    const nameErrorMessage = document.getElementById('name-error-message');
    const descErrorMessage = document.getElementById('desc-error-message');
    const nameCharCounter = document.getElementById('name-char-counter');
    const descCharCounter = document.getElementById('desc-char-counter');
    const addHabitBtn = document.getElementById('add-habit-btn');

    // DOM Elements - Habits Container & States
    const habitsContainer = document.getElementById('habits-container');
    const emptyState = document.getElementById('empty-state');
    const loadingState = document.getElementById('loading-state');

    // DOM Elements - Delete Modal
    const deleteModal = document.getElementById('delete-modal');
    const modalBodyText = document.getElementById('modal-body-text');
    const modalCancelBtn = document.getElementById('modal-cancel-btn');
    const modalConfirmBtn = document.getElementById('modal-confirm-btn');

    // DOM Elements - Toast Container
    const toastContainer = document.getElementById('toast-container');

    // State
    let habitsList = [];
    let habitToDelete = null;

    // -------------------------------------------------------------
    // INITIALIZATION
    // -------------------------------------------------------------

    function init() {
        displayCurrentDate();
        setupEventListeners();
        loadHabits();
    }

    function displayCurrentDate() {
        const today = new Date();
        const options = { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' };
        currentDateText.textContent = today.toLocaleDateString(undefined, options);
    }

    function setupEventListeners() {
        // Form Input Character Counters
        habitNameInput.addEventListener('input', () => {
            const len = habitNameInput.value.length;
            nameCharCounter.textContent = `${len} / 100`;
            if (len > 0) {
                habitNameInput.classList.remove('has-error');
                nameErrorMessage.textContent = '';
            }
        });

        habitDescInput.addEventListener('input', () => {
            const len = habitDescInput.value.length;
            descCharCounter.textContent = `${len} / 300`;
            if (len <= 300) {
                habitDescInput.classList.remove('has-error');
                descErrorMessage.textContent = '';
            }
        });

        // Form Submit
        addHabitForm.addEventListener('submit', handleAddHabit);

        // Delete Modal Actions
        modalCancelBtn.addEventListener('click', closeDeleteModal);
        modalConfirmBtn.addEventListener('click', handleConfirmDelete);

        // Close modal on escape key or clicking backdrop
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && deleteModal.style.display !== 'none') {
                closeDeleteModal();
            }
        });

        deleteModal.addEventListener('click', (e) => {
            if (e.target === deleteModal) {
                closeDeleteModal();
            }
        });
    }

    // -------------------------------------------------------------
    // API OPERATIONS
    // -------------------------------------------------------------

    /**
     * Fetch all habits and stats from backend API
     */
    async function loadHabits() {
        showLoading(true);

        try {
            const response = await fetch('/api/habits');
            if (!response.ok) {
                throw new Error(`Failed to load habits (Status: ${response.status})`);
            }

            const data = await response.json();
            habitsList = data.habits || [];
            updateStatsUI(data.stats);
            renderHabitsList(habitsList);
        } catch (error) {
            console.error('Error fetching habits:', error);
            showToast('Unable to connect to server. Please check if the app is running.', 'error');
            emptyState.style.display = 'flex';
            habitsContainer.style.display = 'none';
        } finally {
            showLoading(false);
        }
    }

    /**
     * Handle adding a new habit
     */
    async function handleAddHabit(e) {
        e.preventDefault();

        const name = habitNameInput.value.trim();
        const description = habitDescInput.value.trim();

        // Validation
        let hasError = false;
        if (!name) {
            habitNameInput.classList.add('has-error');
            nameErrorMessage.textContent = 'Please enter a habit name.';
            habitNameInput.focus();
            hasError = true;
        } else if (name.length > 100) {
            habitNameInput.classList.add('has-error');
            nameErrorMessage.textContent = 'Habit name must not exceed 100 characters.';
            hasError = true;
        }

        if (description.length > 300) {
            habitDescInput.classList.add('has-error');
            descErrorMessage.textContent = 'Description must not exceed 300 characters.';
            hasError = true;
        }

        if (hasError) return;

        // Disable button during submission
        setButtonLoading(addHabitBtn, true, 'Adding...');

        try {
            const response = await fetch('/api/habits', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });

            const result = await response.json();

            if (!response.ok) {
                showToast(result.error || 'Failed to add habit.', 'error');
                return;
            }

            // Success: Reset form and refresh list
            showToast(`Added habit: "${result.habit.name}"`, 'success');
            habitNameInput.value = '';
            habitDescInput.value = '';
            nameCharCounter.textContent = '0 / 100';
            descCharCounter.textContent = '0 / 300';
            habitNameInput.classList.remove('has-error');
            habitDescInput.classList.remove('has-error');
            nameErrorMessage.textContent = '';
            descErrorMessage.textContent = '';

            await loadHabits();
        } catch (error) {
            console.error('Error adding habit:', error);
            showToast('Network error while adding habit. Please try again.', 'error');
        } finally {
            setButtonLoading(addHabitBtn, false, 'Add Habit');
        }
    }

    /**
     * Toggle today's completion for a habit
     */
    async function handleToggleComplete(habitId, habitName, targetButton) {
        targetButton.disabled = true;

        try {
            const response = await fetch(`/api/habits/${habitId}/complete`, {
                method: 'PATCH'
            });

            const result = await response.json();

            if (!response.ok) {
                showToast(result.error || 'Failed to update habit status.', 'error');
                targetButton.disabled = false;
                return;
            }

            showToast(result.message, result.completed_today ? 'success' : 'info');
            await loadHabits();
        } catch (error) {
            console.error('Error toggling completion:', error);
            showToast('Network error while updating habit. Please try again.', 'error');
            targetButton.disabled = false;
        }
    }

    /**
     * Delete confirmation modal trigger
     */
    function promptDeleteHabit(habit) {
        habitToDelete = habit;
        modalBodyText.textContent = `Are you sure you want to delete "${habit.name}"? All completion history will be permanently erased.`;
        deleteModal.style.display = 'flex';
        modalConfirmBtn.focus();
    }

    function closeDeleteModal() {
        deleteModal.style.display = 'none';
        habitToDelete = null;
    }

    /**
     * Confirm habit deletion
     */
    async function handleConfirmDelete() {
        if (!habitToDelete) return;

        const habitId = habitToDelete.id;
        const habitName = habitToDelete.name;

        setButtonLoading(modalConfirmBtn, true, 'Deleting...');

        try {
            const response = await fetch(`/api/habits/${habitId}`, {
                method: 'DELETE'
            });

            const result = await response.json();

            if (!response.ok) {
                showToast(result.error || 'Failed to delete habit.', 'error');
                return;
            }

            closeDeleteModal();
            showToast(`Deleted habit: "${habitName}"`, 'info');
            await loadHabits();
        } catch (error) {
            console.error('Error deleting habit:', error);
            showToast('Network error while deleting habit. Please try again.', 'error');
        } finally {
            setButtonLoading(modalConfirmBtn, false, 'Delete Habit');
        }
    }

    // -------------------------------------------------------------
    // UI RENDERING & UPDATES
    // -------------------------------------------------------------

    /**
     * Update progress bar, counters, and motivation text
     */
    function updateStatsUI(stats) {
        if (!stats) return;

        const { total, completed_today, completion_percentage } = stats;
        const pending = Math.max(0, total - completed_today);

        // Update counts
        totalHabitsCount.textContent = total;
        completedHabitsCount.textContent = completed_today;
        pendingHabitsCount.textContent = pending;
        habitsCounterPill.textContent = `${total} ${total === 1 ? 'habit' : 'habits'}`;

        // Update progress bar
        const percentage = Math.round(completion_percentage);
        percentageBadge.textContent = `${percentage}%`;
        progressBarFill.style.width = `${percentage}%`;
        progressBarWrapper.setAttribute('aria-valuenow', percentage);

        // Motivation message
        if (total === 0) {
            statsMotivationText.textContent = 'Add your first habit below to begin tracking!';
        } else if (percentage === 0) {
            statsMotivationText.textContent = 'Ready to conquer the day? Check off your first habit!';
        } else if (percentage < 50) {
            statsMotivationText.textContent = 'Nice momentum! Keep the progress going.';
        } else if (percentage < 100) {
            statsMotivationText.textContent = 'More than halfway there! Almost finished for today.';
        } else {
            statsMotivationText.textContent = 'Outstanding work! All habits crushed today! 🎉';
        }
    }

    /**
     * Render list of habit cards
     */
    function renderHabitsList(habits) {
        habitsContainer.innerHTML = '';

        if (!habits || habits.length === 0) {
            emptyState.style.display = 'flex';
            habitsContainer.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        habitsContainer.style.display = 'grid';

        habits.forEach(habit => {
            const card = document.createElement('article');
            card.className = `habit-card ${habit.completed_today ? 'is-completed' : ''}`;
            card.id = `habit-card-${habit.id}`;

            // Format creation date
            let formattedDate = habit.created_at;
            try {
                const dateObj = new Date(habit.created_at);
                if (!isNaN(dateObj)) {
                    formattedDate = dateObj.toLocaleDateString(undefined, {
                        month: 'short',
                        day: 'numeric'
                    });
                }
            } catch (e) {
                formattedDate = habit.created_at;
            }

            // Status Badge
            const statusBadgeHtml = habit.completed_today
                ? `<span class="habit-status-badge badge-completed">✓ Completed Today</span>`
                : `<span class="habit-status-badge badge-pending">○ Pending Today</span>`;

            // Toggle Button
            const toggleButtonHtml = habit.completed_today
                ? `<button type="button" class="btn btn-toggle-undo" data-id="${habit.id}" aria-label="Undo completion for ${escapeHtml(habit.name)}">
                     <span>↩ Undo</span>
                   </button>`
                : `<button type="button" class="btn btn-toggle-done" data-id="${habit.id}" aria-label="Mark ${escapeHtml(habit.name)} as completed">
                     <span>✓ Mark Done</span>
                   </button>`;

            card.innerHTML = `
                <div class="habit-header">
                    <div class="habit-title-group">
                        <h3 class="habit-name">${escapeHtml(habit.name)}</h3>
                        ${habit.description ? `<p class="habit-desc">${escapeHtml(habit.description)}</p>` : ''}
                        ${statusBadgeHtml}
                    </div>
                </div>

                <div class="habit-meta-row">
                    <span>Added ${formattedDate}</span>
                    <span>🔥 ${habit.total_completions} ${habit.total_completions === 1 ? 'completion' : 'completions'}</span>
                </div>

                <div class="habit-actions-row">
                    ${toggleButtonHtml}
                    <button type="button" class="btn-icon-delete" data-id="${habit.id}" aria-label="Delete habit ${escapeHtml(habit.name)}" title="Delete habit">
                        <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="3 6 5 6 21 6"></polyline>
                            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                            <line x1="10" y1="11" x2="10" y2="17"></line>
                            <line x1="14" y1="11" x2="14" y2="17"></line>
                        </svg>
                    </button>
                </div>
            `;

            // Attach toggle event
            const toggleBtn = card.querySelector('.btn-toggle-done, .btn-toggle-undo');
            toggleBtn.addEventListener('click', () => {
                handleToggleComplete(habit.id, habit.name, toggleBtn);
            });

            // Attach delete event
            const deleteBtn = card.querySelector('.btn-icon-delete');
            deleteBtn.addEventListener('click', () => {
                promptDeleteHabit(habit);
            });

            habitsContainer.appendChild(card);
        });
    }

    // -------------------------------------------------------------
    // HELPERS & NOTIFICATIONS
    // -------------------------------------------------------------

    function showLoading(isLoading) {
        if (isLoading) {
            loadingState.style.display = 'grid';
            emptyState.style.display = 'none';
            habitsContainer.style.display = 'none';
        } else {
            loadingState.style.display = 'none';
        }
    }

    function setButtonLoading(button, isLoading, text) {
        button.disabled = isLoading;
        const textSpan = button.querySelector('span');
        if (textSpan) {
            textSpan.textContent = text;
        } else {
            button.textContent = text;
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    /**
     * Display a floating toast message
     * @param {string} message - Message text
     * @param {'success'|'error'|'info'} type - Toast type
     */
    function showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;

        const icons = {
            success: '✅',
            error: '⚠️',
            info: 'ℹ️'
        };

        toast.innerHTML = `
            <span class="toast-icon">${icons[type] || 'ℹ️'}</span>
            <span class="toast-message">${escapeHtml(message)}</span>
        `;

        toastContainer.appendChild(toast);

        // Auto-remove after 3.5 seconds
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(16px)';
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 3500);
    }

    // Run app
    init();
});
