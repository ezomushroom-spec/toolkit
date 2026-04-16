/**
 * Post Manager - Frontend Script
 * API通信とUI操作を管理
 */

// ==============================
// 状態管理
// ==============================

const state = {
    tasks: [],
    settings: {},
    isProcessing: false,
    isMutatingTasks: false,
    isSavingSettings: false,
    editingTaskIndex: -1,
    ws: null,
    currentProcessId: null,
    runtime: {
        execution: {
            active: false,
            status: 'idle',
            step: '',
            kind: '',
            message: '',
            message_level: 'info',
            process_id: null,
            elapsed_seconds: 0
        },
        active_processes: [],
        recent_processes: [],
        web_run_all_steps: ['clean', 'mega', 'discord']
    },
    runtimePollTimer: null,
    seenProcessEvents: new Set(),
    connectionWarningVisible: false,
    pixivTagSuggestTimer: null,
    pixivTagRequestToken: 0,
    pixivTagExpanded: false,
    pixivTagContentTab: '',
    pixivTagQuery: ''
};

const desktopBridge = window.postManagerDesktop || null;

// ==============================
// API通信
// ==============================

const API = {
    baseUrl: '',

    async request(endpoint, options = {}) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers
                },
                ...options
            });

            if (!response.ok) {
                let message = `HTTP ${response.status}`;
                let errorPayload = null;
                try {
                    errorPayload = await response.json();
                    if (errorPayload.detail) {
                        message = typeof errorPayload.detail === 'string'
                            ? errorPayload.detail
                            : JSON.stringify(errorPayload.detail);
                    } else if (errorPayload.message) {
                        message = errorPayload.message;
                    }
                } catch (parseError) {
                    // ignore parse error and keep status-based message
                }
                const apiError = new Error(message);
                apiError.status = response.status;
                apiError.payload = errorPayload;
                throw apiError;
            }

            return await response.json();
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    },

    async getTasks() {
        return this.request('/api/tasks');
    },

    async addTask(task) {
        return this.request('/api/tasks', {
            method: 'POST',
            body: JSON.stringify(task)
        });
    },

    async updateTask(index, task) {
        return this.request(`/api/tasks/${index}`, {
            method: 'PUT',
            body: JSON.stringify(task)
        });
    },

    async deleteTask(index) {
        return this.request(`/api/tasks/${index}`, {
            method: 'DELETE'
        });
    },

    async runStep(step) {
        return this.request(`/api/run/${step}`, {
            method: 'POST'
        });
    },

    async getStatus() {
        return this.request('/api/status');
    },

    async getRuntimeStatus() {
        return this.request('/api/runtime-status');
    },

    async getSettings() {
        return this.request('/api/settings');
    },

    async updateSettings(settings) {
        return this.request('/api/settings', {
            method: 'PUT',
            body: JSON.stringify(settings)
        });
    },

    async browseFolders(path = '') {
        return this.request(`/api/browse?path=${encodeURIComponent(path)}`);
    },

    async validateFolder(path) {
        return this.request('/api/validate-folder', {
            method: 'POST',
            body: JSON.stringify({ path })
        });
    },

    async getProcessStatus(processId) {
        return this.request(`/api/process/${processId}`);
    },

    async stopProcess(processId) {
        return this.request(`/api/process/${processId}`, {
            method: 'DELETE'
        });
    },

    async getPixivTagSuggestions(params = {}) {
        const query = new URLSearchParams(params);
        return this.request(`/api/pixiv-tags/suggest?${query.toString()}`);
    }
};

// ==============================
// UI操作
// ==============================

const UI = {
    elements: {},

    init() {
        // 要素キャッシュ
        this.elements = {
            tasksContainer: document.getElementById('tasks-container'),
            emptyState: document.getElementById('empty-state'),
            emptyStateHint: document.getElementById('empty-state-hint'),
            summaryTotal: document.getElementById('summary-total'),
            summaryCompleted: document.getElementById('summary-completed'),
            summaryPending: document.getElementById('summary-pending'),
            logContainer: document.getElementById('log-container'),
            progressContainer: document.getElementById('progress-container'),
            progressFill: document.getElementById('progress-fill'),
            progressText: document.getElementById('progress-text'),
            connectionStatus: document.getElementById('connection-status'),
            executionStatus: document.getElementById('execution-status'),
            executionStatusText: document.getElementById('execution-status-text'),
            executionStatusMeta: document.getElementById('execution-status-meta'),
            executionStatusHint: document.getElementById('execution-status-hint'),
            stopProcessBtn: document.getElementById('stop-process-btn'),
            actionButtons: Array.from(document.querySelectorAll('.btn-action')),
            runAllBtn: document.getElementById('run-all-btn'),
            refreshBtn: document.getElementById('refresh-btn'),
            taskDropLauncher: document.getElementById('task-drop-launcher'),
            taskDropHint: document.getElementById('task-drop-hint'),
            addTaskBtn: document.getElementById('add-task-btn'),
            emptyAddTaskBtn: document.getElementById('empty-add-task-btn'),
            saveSettingsBtn: document.getElementById('save-settings-btn'),
            pixivTagInput: document.getElementById('edit-tags'),
            pixivTagSuggestions: document.getElementById('pixiv-tag-suggestions'),
            pixivTagStatus: document.getElementById('pixiv-tag-status'),
            pixivTagQueryInput: document.getElementById('pixiv-tag-query'),
            pixivTagBrowserModal: document.getElementById('pixiv-tag-browser-modal'),
            openPixivTagBrowserBtn: document.getElementById('open-pixiv-tag-browser-btn'),
            editTaskModal: document.getElementById('edit-task-modal'),
            editTaskForm: document.getElementById('edit-task-form'),
            settingsForm: document.getElementById('settings-form')
        };

        // イベントリスナー設定
        this.setupEventListeners();
        this.updateTaskDropHint();
        this.updateEmptyStateDropHint();
        this.setupPixivTagSupport();

        // 初期データ読み込み
        this.loadTasks();
        this.loadSettings();

        // サーバー接続確認
        this.checkConnection();
        this.startRuntimePolling();
    },

    setupEventListeners() {
        // タブ切り替え
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.switchTab(btn.dataset.tab);
            });
        });

        // 更新ボタン
        this.elements.refreshBtn?.addEventListener('click', () => {
            this.loadTasks();
        });

        // タスク追加ランチャー
        this.setupTaskDropLauncher();
        this.setupEmptyStateDropZone();
        this.elements.emptyAddTaskBtn?.addEventListener('click', () => {
            this.requestAddTask();
        });

        // モーダル閉じる
        document.querySelectorAll('.modal-close, .modal-cancel, .modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                const modal = e.target.closest('.modal');
                if (!modal) {
                    return;
                }
                if (e.target.classList.contains('modal-overlay') ||
                    e.target.classList.contains('modal-close') ||
                    e.target.classList.contains('modal-cancel')) {
                    this.hideModal(modal.id);
                }
            });
        });

        // タスク編集フォーム
        this.elements.editTaskForm?.addEventListener('submit', async (e) => {
            e.preventDefault();
            await this.handleSaveTask(e.target);
        });

        // アクションボタン
        this.elements.actionButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                const step = btn.dataset.step;
                await this.runStep(step);
            });
        });

        // 全ステップ実行
        this.elements.runAllBtn?.addEventListener('click', async () => {
            await this.runAllSteps();
        });

        this.elements.stopProcessBtn?.addEventListener('click', async () => {
            await this.stopCurrentProcess();
        });

        // ログクリア
        document.getElementById('clear-log-btn')?.addEventListener('click', () => {
            this.elements.logContainer.innerHTML = '';
            this.log('ログをクリアしました', 'info');
        });

        // 設定保存
        this.elements.saveSettingsBtn?.addEventListener('click', async () => {
            if (state.isProcessing) {
                this.log('処理中は設定保存できません。完了後に再度お試しください。', 'warning');
                return;
            }
            await this.handleSaveSettings();
        });

        document.addEventListener('click', async (event) => {
            const addBtn = event.target.closest('#empty-add-task-btn, #add-task-btn');
            if (addBtn) {
                event.preventDefault();
                if (this.elements.editTaskModal && !this.elements.editTaskModal.classList.contains('hidden')) {
                    return;
                }
                await this.requestAddTask();
                return;
            }

            const editBtn = event.target.closest('.task-edit');
            if (editBtn) {
                event.preventDefault();
                const index = Number(editBtn.dataset.index);
                if (!Number.isNaN(index)) {
                    this.openEditModal(index);
                }
            }
        });
    },

    setupPixivTagSupport() {
        this.elements.openPixivTagBrowserBtn?.addEventListener('click', () => {
            this.openPixivTagBrowser();
        });

        this.elements.pixivTagQueryInput?.addEventListener('input', (event) => {
            state.pixivTagQuery = event.target.value || '';
            this.queuePixivTagSuggestions();
        });

        document.querySelector('.pixiv-tag-browser-close')?.addEventListener('click', () => {
            this.hideModal('pixiv-tag-browser-modal');
        });
    },

    setupTaskDropLauncher() {
        const launcher = this.elements.taskDropLauncher;
        if (!launcher) {
            return;
        }

        launcher.addEventListener('click', () => {
            this.requestAddTask();
        });

        launcher.addEventListener('keydown', (event) => {
            if (event.key !== 'Enter' && event.key !== ' ') {
                return;
            }
            event.preventDefault();
            this.requestAddTask();
        });

        launcher.addEventListener('dragover', (event) => {
            event.preventDefault();
            launcher.classList.add('drag-over');
        });

        launcher.addEventListener('dragleave', (event) => {
            if (event.currentTarget && event.currentTarget.contains(event.relatedTarget)) {
                return;
            }
            launcher.classList.remove('drag-over');
        });

        launcher.addEventListener('drop', async (event) => {
            event.preventDefault();
            launcher.classList.remove('drag-over');
            await this.handleTaskLauncherDrop(event.dataTransfer);
        });
    },

    updateTaskDropHint() {
        if (!this.elements.taskDropHint) {
            return;
        }

        this.elements.taskDropHint.textContent = desktopBridge && typeof desktopBridge.pickFolder === 'function'
            ? 'または追加'
            : 'または追加';
    },

    setupEmptyStateDropZone() {
        const emptyState = this.elements.emptyState;
        if (!emptyState) {
            return;
        }

        emptyState.classList.add('drop-target');

        emptyState.addEventListener('dragover', (event) => {
            event.preventDefault();
            emptyState.classList.add('drag-over');
        });

        emptyState.addEventListener('dragleave', (event) => {
            if (event.currentTarget && event.currentTarget.contains(event.relatedTarget)) {
                return;
            }
            emptyState.classList.remove('drag-over');
        });

        emptyState.addEventListener('drop', async (event) => {
            event.preventDefault();
            emptyState.classList.remove('drag-over');
            await this.handleTaskLauncherDrop(event.dataTransfer);
        });
    },

    updateEmptyStateDropHint() {
        if (!this.elements.emptyStateHint) {
            return;
        }

        this.elements.emptyStateHint.textContent = desktopBridge && typeof desktopBridge.pickFolder === 'function'
            ? 'フォルダをドロップして開始'
            : 'ドロップまたは追加';
    },

    // タブ切り替え
    switchTab(tabId) {
        // タブボタンの状態更新
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabId);
        });

        // タブコンテンツの表示切替
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `tab-${tabId}`);
        });
    },

    async loadTasks() {
        try {
            this.log('タスクを読み込み中...', 'info');
            const data = await API.getTasks();
            const synced = this.syncTasksFromPayload(data);
            this.log(
                synced
                    ? `${state.tasks.length}件のタスクを読み込みました`
                    : 'タスク一覧の形式が想定と異なります',
                synced ? 'success' : 'warning'
            );
        } catch (error) {
            this.log(`タスクの読み込みに失敗しました: ${error.message}`, 'error');
        }
    },

    syncTasksFromPayload(payload) {
        if (!payload || !Array.isArray(payload.tasks)) {
            return false;
        }

        state.tasks = payload.tasks;
        this.renderTasks();
        return true;
    },

    renderTasks() {
        const container = this.elements.tasksContainer;
        const taskLocked = this.isTaskMutationLocked();
        const completedCount = state.tasks.filter(task => !!task.zip_url).length;
        const pendingCount = Math.max(state.tasks.length - completedCount, 0);

        this.elements.summaryTotal.textContent = String(state.tasks.length);
        this.elements.summaryCompleted.textContent = String(completedCount);
        this.elements.summaryPending.textContent = String(pendingCount);

        if (state.tasks.length === 0) {
            this.elements.emptyState.classList.remove('hidden');
            container.querySelectorAll('.task-item').forEach(el => el.remove());
            this.refreshActionAvailability();
            return;
        }

        this.elements.emptyState.classList.add('hidden');
        container.querySelectorAll('.task-item').forEach(el => el.remove());

        state.tasks.forEach((task, index) => {
            const taskEl = document.createElement('div');
            taskEl.className = 'task-item';
            taskEl.innerHTML = `
                <div class="task-leading">
                    <input type="checkbox" class="task-checkbox" checked disabled aria-hidden="true">
                </div>
                <div class="task-main">
                    <div class="task-row">
                        <div class="task-info">
                            <div class="task-title">${this.escapeHtml(task.title || '(無題)')}</div>
                            <div class="task-folder">${this.escapeHtml(task.target_folder || 'フォルダ未設定')}</div>
                        </div>
                        <span class="task-status ${task.zip_url ? 'completed' : 'pending'}">
                            ${task.zip_url ? '完了' : '未処理'}
                        </span>
                    </div>
                    <div class="task-meta">${this.buildTaskMeta(task)}</div>
                    <div class="task-footer">
                        <span class="task-guidance">${this.buildTaskGuidance(task)}</span>
                        <div class="task-actions">
                            <button type="button" class="btn btn-secondary btn-task-action task-edit" data-index="${index}" ${taskLocked ? 'disabled' : ''}>編集</button>
                            <button type="button" class="btn btn-secondary btn-task-action btn-danger-soft task-delete" data-index="${index}" ${taskLocked ? 'disabled' : ''}>削除</button>
                        </div>
                    </div>
                </div>
            `;

            // 編集ボタン
            taskEl.querySelector('.task-edit').addEventListener('click', (e) => {
                e.stopPropagation();
                this.openEditModal(index);
            });

            // 削除ボタン
            taskEl.querySelector('.task-delete').addEventListener('click', async (e) => {
                e.stopPropagation();
                await this.deleteTask(index);
            });
            container.appendChild(taskEl);
        });
        this.refreshActionAvailability();
    },

    async handleTaskLauncherDrop(dataTransfer) {
        if (state.isProcessing || this.isTaskMutationLocked()) {
            this.log('処理中はタスク追加できません。完了後に再度お試しください。', 'warning');
            return;
        }

        const path = await FolderBrowser.extractDroppedPath(dataTransfer);
        if (!path) {
            this.log(
                desktopBridge
                    ? 'D&D から有効なフォルダを取得できませんでした。空の新規タスクを開きます。'
                    : '標準ブラウザでは D&D からパスを取得できない場合があります。新規タスクを開きます。',
                'warning'
            );
            this.requestAddTask();
            return;
        }

        await this.requestAddTask({
            target_folder: path,
            title: this.suggestTaskTitleFromPath(path)
        });
        this.log(`フォルダを受け取りました: ${path}`, 'success');
    },

    suggestTaskTitleFromPath(pathValue) {
        const trimmed = (pathValue || '').replace(/[\\/]+$/, '');
        const segments = trimmed.split(/[\\/]/).filter(Boolean);
        return segments.length > 0 ? segments[segments.length - 1] : '';
    },

    async requestAddTask(prefill = null) {
        if (state.isProcessing || this.isTaskMutationLocked()) {
            this.log('処理中はタスク追加できません。完了後に再度お試しください。', 'warning');
            return;
        }
        this.openEditModal(-1, prefill);

        if (prefill && prefill.target_folder) {
            await FolderBrowser.validatePath(prefill.target_folder);
        }
    },

    // 編集モーダルを開く
    openEditModal(index, draftTask = null) {
        if (this.isTaskMutationLocked()) {
            this.log('処理中はタスク編集できません。完了後に再度お試しください。', 'warning');
            return;
        }
        if (!this.elements.editTaskForm) {
            this.log('タスク編集フォームが見つかりません。画面を再読み込みしてください。', 'error');
            return;
        }
        state.pixivTagQuery = '';
        if (this.elements.pixivTagQueryInput) {
            this.elements.pixivTagQueryInput.value = '';
        }
        if (this.elements.pixivTagBrowserModal && !this.elements.pixivTagBrowserModal.classList.contains('hidden')) {
            this.hideModal('pixiv-tag-browser-modal');
        }
        state.editingTaskIndex = index;
        const form = this.elements.editTaskForm;

        if (index >= 0 && state.tasks[index]) {
            // 既存タスクの編集
            const task = state.tasks[index];
            form.querySelector('#edit-task-index').value = index;
            form.querySelector('#edit-title').value = task.title || '';
            form.querySelector('#edit-folder').value = task.target_folder || '';
            form.querySelector('#edit-tags').value = task.tags || '';

            // scheduleを日付と時間に分解 (YYYY/MM/DD HH:MM or YYYY-MM-DDTHH:MM)
            // 新しいUI（日付+時間分離）と古いUI（datetime-local）の両方に対応
            const scheduleDateInput = form.querySelector('#edit-schedule-date');
            const scheduleTimeInput = form.querySelector('#edit-schedule-time');
            const scheduleLegacyInput = form.querySelector('#edit-schedule'); // 古い形式用

            try {
                const schedule = task.schedule || '';
                if (scheduleDateInput && scheduleTimeInput) {
                    // 新しいUI形式
                    if (schedule) {
                        let datePart = '';
                        let timePart = '';
                        if (schedule.includes('T')) {
                            [datePart, timePart] = schedule.split('T');
                        } else if (schedule.includes(' ')) {
                            [datePart, timePart] = schedule.split(' ');
                            datePart = datePart.replace(/\//g, '-');
                        } else if (schedule.includes('/') || schedule.includes('-')) {
                            datePart = schedule.replace(/\//g, '-');
                        }
                        scheduleDateInput.value = datePart;
                        if (timePart) {
                            scheduleTimeInput.value = timePart.slice(0, 5);
                        } else {
                            scheduleTimeInput.value = '';
                        }
                    } else {
                        scheduleDateInput.value = '';
                        scheduleTimeInput.value = '';
                    }
                } else if (scheduleLegacyInput) {
                    // 古いUI形式（datetime-local）への後方互換性
                    scheduleLegacyInput.value = schedule || '';
                }
            } catch (e) {
                console.error('Schedule parse error:', e);
            }

            form.querySelector('#edit-caption-pixiv').value = task.caption_pixiv || '';
            form.querySelector('#edit-caption-patreon').value = task.caption_patreon || '';
            form.querySelector('#edit-caption-discord').value = task.caption_discord || '';
            form.querySelector('#edit-patreon-tier').value = task.patreon_tier || '';
            form.querySelector('#edit-discord-channel').value = task.discord_channel || '';
            form.querySelector('#edit-zip-password').value = task.zip_password || '';
            form.querySelector('#edit-zip-url').value = task.zip_url || '';
        } else {
            // 新規作成
            form.reset();
            form.querySelector('#edit-task-index').value = -1;
            if (draftTask) {
                form.querySelector('#edit-title').value = draftTask.title || '';
                form.querySelector('#edit-folder').value = draftTask.target_folder || '';
                form.querySelector('#edit-tags').value = draftTask.tags || '';
            }
        }

        this.showModal('edit-task-modal');
    },

    async handleSaveTask(form) {
        if (this.isTaskMutationLocked()) {
            this.log('処理中はタスク保存できません。完了後に再度お試しください。', 'warning');
            return;
        }
        const formData = new FormData(form);

        // 日付と時間を結合してPixiv形式(YYYY/MM/DD HH:MM)に
        // 新しいUI形式と古いUI形式（datetime-local）の両方に対応
        let schedule = '';
        const scheduleDate = formData.get('schedule_date');
        const scheduleTime = formData.get('schedule_time');
        const scheduleLegacy = formData.get('schedule'); // 古い形式用

        if (scheduleDate) {
            // 新しいUI形式
            const dateStr = scheduleDate.replace(/-/g, '/');
            schedule = scheduleTime ? `${dateStr} ${scheduleTime}` : dateStr;
        } else if (scheduleLegacy) {
            // 古いUI形式（datetime-local）
            schedule = scheduleLegacy;
        }

        const task = {
            title: formData.get('title'),
            target_folder: formData.get('target_folder'),
            tags: formData.get('tags') || '',
            schedule: schedule,
            caption_pixiv: formData.get('caption_pixiv') || '',
            caption_patreon: formData.get('caption_patreon') || '',
            caption_discord: formData.get('caption_discord') || '',
            patreon_tier: formData.get('patreon_tier') || '',
            discord_channel: formData.get('discord_channel') || '',
            zip_password: formData.get('zip_password') || '',
            zip_url: formData.get('zip_url') || ''
        };

        const index = parseInt(formData.get('index'));

        state.isMutatingTasks = true;
        this.refreshActionLockState();
        try {
            let result;
            if (index >= 0) {
                // 更新
                result = await API.updateTask(index, task);
                this.log(result.message || `タスク「${task.title}」を更新しました`, 'success');
            } else {
                // 新規作成
                result = await API.addTask(task);
                this.log(result.message || `タスク「${task.title}」を追加しました`, 'success');
            }
            if (result.learning_warning) {
                this.log(result.learning_warning, 'warning');
            }
            if (!this.syncTasksFromPayload(result)) {
                await this.loadTasks();
            }
            this.hideModal('edit-task-modal');
        } catch (error) {
            this.log(`タスクの保存に失敗しました: ${error.message}`, 'error');
        } finally {
            state.isMutatingTasks = false;
            this.refreshActionLockState();
        }
    },

    async deleteTask(index) {
        if (this.isTaskMutationLocked()) {
            this.log('処理中はタスク削除できません。完了後に再度お試しください。', 'warning');
            return;
        }
        const task = state.tasks[index] || {};
        const taskLabel = task.title || task.target_folder || '(無題)';
        if (!confirm(`このタスクを削除しますか？\n対象: ${taskLabel}`)) return;

        state.isMutatingTasks = true;
        this.refreshActionLockState();
        try {
            const result = await API.deleteTask(index);
            this.log(result.message || 'タスクを削除しました', 'success');
            if (!this.syncTasksFromPayload(result)) {
                await this.loadTasks();
            }
        } catch (error) {
            this.log(`削除に失敗しました: ${error.message}`, 'error');
        } finally {
            state.isMutatingTasks = false;
            this.refreshActionLockState();
        }
    },

    // 設定の読み込み
    async loadSettings() {
        try {
            const settings = await API.getSettings();
            state.settings = settings;

            const form = this.elements.settingsForm;
            form.querySelector('#mega-email').value = settings.mega_email || '';
            form.querySelector('#mega-password').placeholder = settings.mega_password_masked || '●●●●●●●●';
            form.querySelector('#discord-webhook').value = settings.discord_webhook_url || '';
            form.querySelector('#template-pixiv').value = settings.template_pixiv || '{caption_pixiv}';
            form.querySelector('#template-patreon').value = settings.template_patreon || '{caption_patreon}';
            form.querySelector('#template-discord').value = settings.template_discord || '{caption_discord}';
        } catch (error) {
            console.error('Settings load error:', error);
        }
    },

    async handleSaveSettings() {
        if (state.isProcessing || state.isSavingSettings) {
            this.log('処理中は設定保存できません。完了後に再度お試しください。', 'warning');
            return;
        }
        const form = this.elements.settingsForm;
        const settings = {
            mega_email: form.querySelector('#mega-email').value,
            mega_password: form.querySelector('#mega-password').value,
            discord_webhook_url: form.querySelector('#discord-webhook').value,
            template_pixiv: form.querySelector('#template-pixiv').value,
            template_patreon: form.querySelector('#template-patreon').value,
            template_discord: form.querySelector('#template-discord').value
        };

        state.isSavingSettings = true;
        this.refreshActionLockState();
        try {
            await API.updateSettings(settings);
            this.log('設定を保存しました', 'success');
            // パスワードフィールドをクリア
            form.querySelector('#mega-password').value = '';
            await this.loadSettings();
        } catch (error) {
            this.log(`設定の保存に失敗しました: ${error.message}`, 'error');
        } finally {
            state.isSavingSettings = false;
            this.refreshActionLockState();
        }
    },

    async runStep(step) {
        await this.refreshRuntimeStatus();
        if (state.runtime.execution.active || state.isProcessing) {
            this.log('処理中です。完了までお待ちください。', 'warning');
            return { success: false, blocked: true, reason: 'busy' };
        }

        const stepNames = {
            clean: 'Clean & Zip',
            mega: 'MEGA Upload',
            pixiv: 'Pixiv',
            patreon: 'Patreon',
            discord: 'Discord'
        };

        state.isProcessing = true;
        this.setControlsDisabled(true);
        this.log(`${stepNames[step]} を実行中...`, 'info');
        this.showProgress(0);

        try {
            const result = await API.runStep(step);

            if (result.success) {
                this.log(`${stepNames[step]}: ${result.message}`, 'success');

                // Pixiv/Patreonの場合は追加案内
                if (result.requires_user_action && result.process_id) {
                    state.currentProcessId = result.process_id;
                    this.log('📌 ブラウザウィンドウが開きました。投稿内容を確認し、ブラウザ上の「投稿」ボタンをクリックしてください。', 'info');
                    this.log(`🔄 プロセスID: ${result.process_id}`, 'info');
                }
                if (result.runtime) {
                    this.applyRuntimeState(result.runtime);
                }
            } else {
                this.log(`${stepNames[step]}: ${result.message}`, 'warning');
                if (result.runtime) {
                    this.applyRuntimeState(result.runtime);
                }
            }
            this.showProgress(100);
            return result;
        } catch (error) {
            this.log(`${stepNames[step]} に失敗しました: ${error.message}`, 'error');
            return { success: false, message: error.message };
        } finally {
            await this.refreshRuntimeStatus();
            state.isProcessing = state.runtime.execution.active;
            if (!state.runtime.execution.active) {
                setTimeout(() => this.hideProgress(), 2000);
            }
            await this.loadTasks();
        }
    },

    async runAllSteps() {
        await this.refreshRuntimeStatus();
        if (state.runtime.execution.active || state.isProcessing) {
            this.log('処理中です。完了までお待ちください。', 'warning');
            return;
        }

        const steps = state.runtime.web_run_all_steps || ['clean', 'mega', 'discord'];
        let completed = 0;

        this.log('前処理まとめ実行を開始します...', 'info');
        this.showProgress(0);
        state.isProcessing = true;
        let abortedReason = '';

        for (const step of steps) {
            const result = await this.runStep(step);
            if (state.runtime.execution.active) {
                this.log('別処理が継続中のため、全ステップ実行を中断します。', 'warning');
                abortedReason = '別処理が継続中です。';
                break;
            }
            if (!result?.success) {
                abortedReason = result?.message || `${step} で失敗しました。`;
                this.log(`前処理まとめ実行を中断しました: ${abortedReason}`, 'error');
                state.isProcessing = false;
                return;
            }
            completed++;
            this.showProgress((completed / steps.length) * 100);
        }

        if (!state.runtime.execution.active) {
            this.log(
                abortedReason
                    ? `前処理まとめ実行を終了しました: ${abortedReason}`
                    : '前処理まとめ実行が完了しました',
                abortedReason ? 'warning' : 'success'
            );
            state.isProcessing = false;
        }
    },

    async checkConnection() {
        try {
            const status = await API.getStatus();
            this.setConnectionStatus(true);
            state.connectionWarningVisible = false;
            if (status.runtime) {
                this.applyRuntimeState(status.runtime);
            }
        } catch {
            this.setConnectionStatus(false);
            if (!state.connectionWarningVisible) {
                this.log('サーバーに接続できません。再読み込みするか、起動バッチを確認してください。', 'warning');
                state.connectionWarningVisible = true;
            }
        }
    },

    startRuntimePolling() {
        if (state.runtimePollTimer) {
            clearInterval(state.runtimePollTimer);
        }
        state.runtimePollTimer = setInterval(() => {
            this.refreshRuntimeStatus();
        }, 3000);
    },

    async refreshRuntimeStatus() {
        try {
            const runtime = await API.getRuntimeStatus();
            this.setConnectionStatus(true);
            state.connectionWarningVisible = false;
            this.applyRuntimeState(runtime);
        } catch (error) {
            this.setConnectionStatus(false);
            if (!state.connectionWarningVisible) {
                this.log('接続が切れました。処理中なら待機し、復旧しない場合は起動バッチを確認してください。', 'warning');
                state.connectionWarningVisible = true;
            }
        }
    },

    applyRuntimeState(runtime) {
        state.runtime = runtime || state.runtime;
        const execution = state.runtime.execution || {};
        const wasBusy = state.isProcessing;
        state.isProcessing = !!execution.active;
        state.currentProcessId = execution.process_id || null;

        this.reportRecentProcesses(state.runtime.recent_processes || []);
        this.updateExecutionStatus(execution);
        this.setControlsDisabled(state.isProcessing);

        if (wasBusy && !state.isProcessing && execution.message) {
            this.log(execution.message, execution.message_level || 'info');
            this.hideProgress();
            this.loadTasks();
        }
    },

    updateExecutionStatus(execution) {
        const box = this.elements.executionStatus;
        const text = this.elements.executionStatusText;
        const meta = this.elements.executionStatusMeta;
        const hint = this.elements.executionStatusHint;
        const stopBtn = this.elements.stopProcessBtn;
        const activeProcesses = state.runtime.active_processes || [];
        const latestRecentProcess = (state.runtime.recent_processes || [])[0];

        if (!execution.active) {
            box.classList.remove('is-busy');
            box.classList.remove('is-warning');
            box.classList.remove('is-error');
            stopBtn.classList.add('hidden');
            this.highlightActiveStep('');

            if (latestRecentProcess) {
                const summary = this.buildRecentProcessSummary(latestRecentProcess);
                box.classList.remove('hidden');
                box.classList.toggle('is-warning', summary.level === 'warning');
                box.classList.toggle('is-error', summary.level === 'error');
                text.textContent = summary.text;
                this.setExecutionStatusMeta(summary.meta);
                this.setExecutionStatusHint(summary.hint);
            } else {
                box.classList.add('hidden');
                text.textContent = '待機中';
                this.setExecutionStatusMeta('');
                this.setExecutionStatusHint('');
            }
            return;
        }

        box.classList.remove('hidden');
        box.classList.add('is-busy');
        box.classList.toggle('is-warning', execution.message_level === 'warning');
        box.classList.toggle('is-error', execution.message_level === 'error');
        const elapsed = execution.elapsed_seconds ? ` (${Math.floor(execution.elapsed_seconds)}s)` : '';
        text.textContent = (execution.message || `${execution.step} を実行中です。`) + elapsed;
        this.setExecutionStatusMeta(this.buildActiveProcessMeta(execution, activeProcesses));
        this.setExecutionStatusHint(this.buildExecutionHint(execution));

        if (execution.kind === 'browser_process' && execution.process_id) {
            stopBtn.classList.remove('hidden');
        } else {
            stopBtn.classList.add('hidden');
        }

        this.highlightActiveStep(execution.step || '');
    },

    setExecutionStatusMeta(message) {
        const meta = this.elements.executionStatusMeta;
        if (!meta) return;
        meta.textContent = message || '';
        meta.classList.toggle('hidden', !message);
    },

    setExecutionStatusHint(message) {
        const hint = this.elements.executionStatusHint;
        if (!hint) return;
        hint.textContent = message || '';
        hint.classList.toggle('hidden', !message);
    },

    getStepLabel(step) {
        const labels = {
            clean: 'Clean & Zip',
            mega: 'MEGA Upload',
            pixiv: 'Pixiv',
            patreon: 'Patreon',
            discord: 'Discord'
        };
        return labels[step] || step || '不明な処理';
    },

    buildActiveProcessMeta(execution, activeProcesses) {
        const parts = [];
        if (execution.step) {
            parts.push(`対象: ${this.getStepLabel(execution.step)}`);
        }
        if (execution.process_id) {
            parts.push(`プロセスID: ${execution.process_id}`);
        }
        if (activeProcesses.length > 1) {
            parts.push(`実行中プロセス: ${activeProcesses.length}件`);
        }
        return parts.join(' / ');
    },

    buildExecutionHint(execution) {
        if (execution.kind === 'browser_process') {
            return '別ウィンドウの内容を確認し、不要なら停止、問題なければブラウザ側の操作を完了してください。';
        }
        if (execution.step === 'clean' || execution.step === 'mega' || execution.step === 'discord') {
            return 'この処理が終わるまでタスク編集と設定保存はロックされます。';
        }
        return '';
    },

    buildRecentProcessSummary(proc) {
        const stepLabel = this.getStepLabel(proc.step);
        const returnCodeText = proc.return_code !== null && proc.return_code !== undefined
            ? ` / code: ${proc.return_code}`
            : '';

        if (proc.status === 'failed') {
            return {
                level: 'error',
                text: `${stepLabel} がエラー終了しました。`,
                meta: `直近プロセスID: ${proc.process_id}${returnCodeText}`,
                hint: 'ログを確認し、起動バッチやブラウザ側の状態を見直してから再試行してください。'
            };
        }

        if (proc.status === 'terminated') {
            return {
                level: 'warning',
                text: `${stepLabel} は途中停止されました。`,
                meta: `直近プロセスID: ${proc.process_id}${returnCodeText}`,
                hint: '未保存の入力が失われている可能性があります。必要ならブラウザ状態を確認してから再開してください。'
            };
        }

        if (proc.status === 'completed') {
            return {
                level: 'info',
                text: `${stepLabel} は完了しています。`,
                meta: `直近プロセスID: ${proc.process_id}${returnCodeText}`,
                hint: '結果を確認し、必要なら次のステップへ進んでください。'
            };
        }

        return {
            level: 'info',
            text: `${stepLabel} の状態を確認しました。`,
            meta: `直近プロセスID: ${proc.process_id}${returnCodeText}`,
            hint: ''
        };
    },

    reportRecentProcesses(recentProcesses) {
        recentProcesses.forEach(proc => {
            const eventKey = `${proc.process_id}:${proc.status}:${proc.return_code ?? ''}`;
            if (state.seenProcessEvents.has(eventKey)) {
                return;
            }

            let message = '';
            let level = 'info';
            if (proc.status === 'completed') {
                message = `${proc.step} プロセスが完了しました。`;
                level = 'success';
            } else if (proc.status === 'failed') {
                message = `${proc.step} プロセスがエラー終了しました。`;
                if (proc.return_code !== null && proc.return_code !== undefined) {
                    message += ` code: ${proc.return_code}`;
                }
                level = 'error';
            } else if (proc.status === 'terminated') {
                message = `${proc.step} プロセスは停止されました。`;
                level = 'warning';
            }

            if (message) {
                state.seenProcessEvents.add(eventKey);
                this.log(message, level);
            }
        });
    },

    setControlsDisabled(disabled) {
        this.refreshActionAvailability(disabled);
        this.refreshActionLockState();
    },

    refreshActionAvailability(forceDisabled = state.isProcessing) {
        const hasTasks = state.tasks.length > 0;
        const shouldDisableActions = forceDisabled || !hasTasks;
        const actionTitle = hasTasks ? '' : '先にタスクを追加してください。';

        this.elements.actionButtons.forEach(btn => {
            btn.disabled = shouldDisableActions;
            btn.title = shouldDisableActions && actionTitle ? actionTitle : '';
        });
        this.elements.runAllBtn.disabled = shouldDisableActions;
        this.elements.runAllBtn.title = shouldDisableActions && actionTitle ? actionTitle : '';
    },

    refreshActionLockState() {
        const taskLocked = this.isTaskMutationLocked();
        this.elements.addTaskBtn.disabled = taskLocked;
        this.elements.emptyAddTaskBtn.disabled = taskLocked;
        this.elements.saveSettingsBtn.disabled = state.isProcessing || state.isSavingSettings;
        document.querySelectorAll('.task-edit, .task-delete').forEach(btn => {
            btn.disabled = taskLocked;
        });
    },

    isTaskMutationLocked() {
        return state.isProcessing || state.isMutatingTasks;
    },

    highlightActiveStep(step) {
        this.elements.actionButtons.forEach(btn => {
            btn.classList.toggle('is-active', btn.dataset.step === step);
        });
    },

    async stopCurrentProcess() {
        if (!state.currentProcessId) return;
        if (!confirm('実行中のブラウザ投稿プロセスを停止しますか？\n保存していない入力内容は失われる場合があります。')) {
            return;
        }

        try {
            this.elements.stopProcessBtn.disabled = true;
            const result = await API.stopProcess(state.currentProcessId);
            if (result.success) {
                this.log('実行中プロセスを停止しました', 'warning');
            } else {
                this.log(`停止に失敗しました: ${result.message}`, 'error');
            }
            await this.refreshRuntimeStatus();
        } catch (error) {
            this.log(`プロセス停止に失敗しました: ${error.message}`, 'error');
        } finally {
            this.elements.stopProcessBtn.disabled = false;
        }
    },

    setConnectionStatus(online) {
        const el = this.elements.connectionStatus;
        el.classList.toggle('online', online);
        el.classList.toggle('offline', !online);
        el.querySelector('.status-text').textContent = online ? '接続中' : 'オフライン';
    },

    log(message, type = 'info') {
        const now = new Date();
        const time = now.toLocaleTimeString('ja-JP', { hour12: false });

        const entry = document.createElement('div');
        entry.className = `log-entry log-${type}`;
        entry.innerHTML = `
            <span class="log-time">${time}</span>
            <span class="log-message">${this.escapeHtml(message)}</span>
        `;

        this.elements.logContainer.appendChild(entry);
        this.elements.logContainer.scrollTop = this.elements.logContainer.scrollHeight;
    },

    showProgress(percent) {
        this.elements.progressContainer.classList.remove('hidden');
        this.elements.progressFill.style.width = `${percent}%`;
        this.elements.progressText.textContent = `${Math.round(percent)}%`;
    },

    hideProgress() {
        this.elements.progressContainer.classList.add('hidden');
        this.elements.progressFill.style.width = '0%';
        this.elements.progressText.textContent = '0%';
    },

    showModal(id) {
        const modal = document.getElementById(id);
        if (!modal) {
            return;
        }
        modal.classList.remove('hidden');
    },

    hideModal(id) {
        const modal = document.getElementById(id);
        if (!modal) {
            return;
        }
        modal.classList.add('hidden');
    },

    openPixivTagBrowser() {
        state.pixivTagExpanded = false;
        state.pixivTagContentTab = '';
        state.pixivTagQuery = this.elements.pixivTagQueryInput?.value || '';
        this.showModal('pixiv-tag-browser-modal');
        this.queuePixivTagSuggestions(true);
        this.elements.pixivTagQueryInput?.focus();
    },

    queuePixivTagSuggestions(immediate = false) {
        if (state.pixivTagSuggestTimer) {
            clearTimeout(state.pixivTagSuggestTimer);
            state.pixivTagSuggestTimer = null;
        }

        const delay = immediate ? 0 : 220;
        state.pixivTagSuggestTimer = setTimeout(() => {
            this.refreshPixivTagSuggestions();
        }, delay);
    },

    async refreshPixivTagSuggestions() {
        const modal = this.elements.pixivTagBrowserModal;
        if (!modal || modal.classList.contains('hidden')) {
            return;
        }
        const tagInput = this.elements.pixivTagInput;

        if (!tagInput) {
            return;
        }

        const requestToken = ++state.pixivTagRequestToken;
        state.pixivTagExpanded = false;
        state.pixivTagContentTab = '';
        this.setPixivTagStatus('タグ一覧を更新中', 'info');

        try {
            const result = await API.getPixivTagSuggestions({
                current_tags: tagInput.value || '',
                browse_vocabulary: '1',
                tag_query: state.pixivTagQuery
            });

            if (requestToken !== state.pixivTagRequestToken) {
                return;
            }

            this.renderPixivTagSuggestions(result.suggestions || []);
        } catch (error) {
            if (requestToken !== state.pixivTagRequestToken) {
                return;
            }
            this.renderPixivTagSuggestions([]);
            this.setPixivTagStatus('候補を取得できません', 'warning');
        }
    },

    renderPixivTagSuggestions(suggestions) {
        const container = this.elements.pixivTagSuggestions;
        const tagInput = this.elements.pixivTagInput;
        if (!container || !tagInput) {
            return;
        }

        const selectedTags = new Set(this.parsePixivTagInput(tagInput.value));
        container.innerHTML = '';

        if (!suggestions.length) {
            this.setPixivTagStatus('一致するタグがありません', 'info');
            return;
        }

        const groupedSuggestions = this.groupPixivTagSuggestions(suggestions);
        const displayState = this.buildPixivTagDisplayState(groupedSuggestions);

        displayState.visibleGroups.forEach(group => {
            const section = document.createElement('section');
            section.className = 'pixiv-tag-group';

            const header = document.createElement('div');
            header.className = 'pixiv-tag-group-header';
            header.innerHTML = `
                <span class="pixiv-tag-group-title">${this.escapeHtml(this.getPixivTagMeaningLabel(group.category))}</span>
                <span class="pixiv-tag-group-count">${group.totalCount}</span>
            `;
            section.appendChild(header);

            if (group.category === 'content' && group.contentDisplay?.subgroups?.length) {
                section.appendChild(this.createPixivTagContentTabs(group.contentDisplay, suggestions));
            }

            const chips = document.createElement('div');
            chips.className = 'pixiv-tag-group-chips';
            group.items.forEach(item => {
                chips.appendChild(this.createPixivTagChip(item, selectedTags));
            });
            section.appendChild(chips);
            container.appendChild(section);
        });

        if (displayState.hiddenCount > 0) {
            const moreBtn = document.createElement('button');
            moreBtn.type = 'button';
            moreBtn.className = 'pixiv-tag-more-btn';
            moreBtn.textContent = state.pixivTagExpanded
                ? '候補をたたむ'
                : `もっと見る (+${displayState.hiddenCount})`;
            moreBtn.addEventListener('click', () => {
                state.pixivTagExpanded = !state.pixivTagExpanded;
                this.renderPixivTagSuggestions(suggestions);
            });
            container.appendChild(moreBtn);
        }

        const suffix = state.pixivTagQuery ? ` "${state.pixivTagQuery}" を検索中` : ' 語彙一覧を表示中';
        this.setPixivTagStatus(state.pixivTagExpanded ? `タグを展開中${suffix}` : `クリックで追加${suffix}`, 'info');
    },

    createPixivTagChip(item, selectedTags) {
        const chip = document.createElement('button');
        const isSelected = selectedTags.has(item.tag);
        chip.type = 'button';
        chip.className = `tag-chip${isSelected ? ' is-selected' : ''}`;
        chip.innerHTML = `
            <span class="tag-chip-label">${this.escapeHtml(item.tag)}</span>
            <span class="tag-chip-source">${this.getPixivTagSourceBadge(item.source)}</span>
        `;
        chip.title = `${this.getPixivTagMeaningLabel(item.meaning_category)} / ${this.getPixivTagSourceLabel(item.source)}`;
        chip.disabled = isSelected;
        chip.addEventListener('click', () => this.appendPixivTag(item.tag));
        return chip;
    },

    groupPixivTagSuggestions(suggestions) {
        const grouped = {
            rating: [],
            work: [],
            character: [],
            content: []
        };

        suggestions.forEach(item => {
            const category = grouped[item.meaning_category] ? item.meaning_category : 'content';
            grouped[category].push(item);
        });

        return grouped;
    },

    buildPixivTagDisplayState(groupedSuggestions) {
        const limits = {
            rating: 1,
            work: 2,
            character: 3,
            content: 2
        };

        let hiddenCount = 0;
        const limitedGroups = {};
        const contentDisplay = this.buildPixivTagContentDisplayState(
            groupedSuggestions.content || [],
            limits.content
        );
        Object.entries(groupedSuggestions).forEach(([category, items]) => {
            if (category === 'content') {
                limitedGroups[category] = contentDisplay.visibleItems;
                hiddenCount += contentDisplay.hiddenCount;
                return;
            }
            const limit = limits[category] ?? items.length;
            if (state.pixivTagExpanded) {
                limitedGroups[category] = items;
                return;
            }
            limitedGroups[category] = items.slice(0, limit);
            hiddenCount += Math.max(items.length - limit, 0);
        });

        return {
            visibleGroups: this.buildPixivTagGroupList(limitedGroups, groupedSuggestions, contentDisplay),
            hiddenCount
        };
    },

    buildPixivTagGroupList(groupedSuggestions, sourceGroups = null, contentDisplay = null) {
        const order = ['rating', 'work', 'character', 'content'];
        const totalGroups = sourceGroups || groupedSuggestions;
        return order
            .map(category => ({
                category,
                items: groupedSuggestions[category] || [],
                totalCount: (totalGroups[category] || []).length,
                contentDisplay: category === 'content' ? contentDisplay : null
            }))
            .filter(group => group.items.length > 0);
    },

    buildPixivTagContentDisplayState(items, limit) {
        const grouped = {
            fetish: [],
            costume: [],
            play: [],
            act: [],
            other: []
        };

        items.forEach(item => {
            const subcategory = grouped[item.content_subcategory] ? item.content_subcategory : 'other';
            grouped[subcategory].push(item);
        });

        const subgroups = this.getPixivTagContentSubcategoryOrder()
            .map(key => ({
                key,
                label: this.getPixivTagContentSubcategoryLabel(key),
                items: grouped[key],
                count: grouped[key].length
            }))
            .filter(group => group.count > 0);

        if (!subgroups.length) {
            state.pixivTagContentTab = '';
            return {
                activeSubcategory: '',
                subgroups: [],
                visibleItems: state.pixivTagExpanded ? items : items.slice(0, limit),
                hiddenCount: state.pixivTagExpanded ? 0 : Math.max(items.length - limit, 0)
            };
        }

        const activeSubcategory = subgroups.some(group => group.key === state.pixivTagContentTab)
            ? state.pixivTagContentTab
            : subgroups[0].key;
        state.pixivTagContentTab = activeSubcategory;

        const activeGroup = subgroups.find(group => group.key === activeSubcategory) || subgroups[0];
        const visibleItems = state.pixivTagExpanded
            ? activeGroup.items
            : activeGroup.items.slice(0, limit);

        return {
            activeSubcategory,
            subgroups,
            visibleItems,
            hiddenCount: state.pixivTagExpanded ? 0 : Math.max(activeGroup.items.length - limit, 0)
        };
    },

    createPixivTagContentTabs(contentDisplay, suggestions) {
        const tabs = document.createElement('div');
        tabs.className = 'pixiv-tag-subtabs';

        contentDisplay.subgroups.forEach(group => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `pixiv-tag-subtab${group.key === contentDisplay.activeSubcategory ? ' is-active' : ''}`;
            button.innerHTML = `
                <span class="pixiv-tag-subtab-label">${this.escapeHtml(group.label)}</span>
                <span class="pixiv-tag-subtab-count">${group.count}</span>
            `;
            button.addEventListener('click', () => {
                state.pixivTagContentTab = group.key;
                state.pixivTagExpanded = false;
                this.renderPixivTagSuggestions(suggestions);
            });
            tabs.appendChild(button);
        });

        return tabs;
    },

    appendPixivTag(tag) {
        const tagInput = this.elements.pixivTagInput;
        if (!tagInput) {
            return;
        }

        const tags = this.parsePixivTagInput(tagInput.value);
        if (!tags.includes(tag)) {
            tags.push(tag);
            tagInput.value = tags.join(' ');
        }
        this.queuePixivTagSuggestions(true);
    },

    parsePixivTagInput(value) {
        return Array.from(new Set((value || '')
            .split(/[\s\u3000]+/)
            .map(tag => tag.trim())
            .filter(Boolean)));
    },

    getPixivTagSourceLabel(source) {
        if (source === 'learning') return '保存時学習';
        if (source === 'history') return '過去の Pixivタグ';
        if (source === 'works') return '作品辞書';
        if (source === 'seed') return '同梱辞書';
        if (source === 'bundle') return '同梱語彙';
        return 'Pixivタグ候補';
    },

    getPixivTagSourceBadge(source) {
        if (source === 'learning') return '学習';
        if (source === 'history') return '履歴';
        if (source === 'works') return '作品';
        if (source === 'seed') return '同梱';
        if (source === 'bundle') return '語彙';
        return '候補';
    },

    getPixivTagMeaningLabel(category) {
        if (category === 'rating') return '年齢区分';
        if (category === 'work') return '作品';
        if (category === 'character') return 'キャラ';
        return '内容候補';
    },

    getPixivTagContentSubcategoryOrder() {
        return ['fetish', 'costume', 'play', 'act', 'other'];
    },

    getPixivTagContentSubcategoryLabel(category) {
        if (category === 'fetish') return '性癖/属性';
        if (category === 'costume') return '衣装';
        if (category === 'play') return 'プレイ';
        if (category === 'act') return '性行為';
        return 'その他';
    },

    setPixivTagStatus(message, level = 'info') {
        const status = this.elements.pixivTagStatus;
        if (!status) {
            return;
        }
        status.textContent = message;
        status.classList.remove('is-warning');
        status.classList.toggle('is-warning', level === 'warning');
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    buildTaskMeta(task) {
        const parts = [];
        if (task.schedule) {
            parts.push(`予約: ${this.escapeHtml(task.schedule)}`);
        }
        if (task.patreon_tier) {
            parts.push(`Patreon: ${this.escapeHtml(task.patreon_tier)}`);
        }
        return parts.length > 0 ? parts.join(' / ') : '必要項目を確認してから実行';
    },

    buildTaskGuidance(task) {
        if (!task.target_folder) {
            return '画像フォルダを設定してください';
        }
        if (!task.zip_url) {
            return '前処理は右側の Clean / MEGA から実行します';
        }
        return 'Pixiv / Patreon はブラウザ確認付きで進めます';
    }
};

// ==============================
// フォルダブラウザ
// ==============================

const FolderBrowser = {
    currentPath: '',
    selectedPath: '',

    init() {
        // 参照ボタン - イベントデリゲーションで対応
        document.addEventListener('click', (e) => {
            if (e.target.id === 'browse-folder-btn' || e.target.closest('#browse-folder-btn')) {
                e.preventDefault();
                this.open();
            }
        });

        // ブラウザモーダルのイベント
        const modal = document.getElementById('folder-browser-modal');
        if (modal) {
            modal.querySelector('.modal-close').addEventListener('click', () => this.close());
            modal.querySelector('.modal-overlay').addEventListener('click', () => this.close());
            modal.querySelector('.folder-browser-cancel').addEventListener('click', () => this.close());
            document.getElementById('folder-select-btn').addEventListener('click', () => this.confirmSelection());
        }

        // D&D設定
        this.setupDropZone();

        // フォルダ入力欄の変更監視
        const folderInput = document.getElementById('edit-folder');
        if (folderInput) {
            folderInput.addEventListener('change', () => this.validatePath(folderInput.value));
            folderInput.addEventListener('blur', () => this.validatePath(folderInput.value));
        }

        this.updateDropZoneHint();

        console.log('FolderBrowser initialized');
    },

    updateDropZoneHint() {
        const hint = document.getElementById('drop-zone-hint');
        const title = document.getElementById('drop-zone-text');
        if (!hint || !title) return;

        if (desktopBridge && typeof desktopBridge.pickFolder === 'function') {
            title.textContent = '📂 推奨: フォルダをここへドロップ';
            hint.textContent = 'D&D または参照';
            return;
        }

        title.textContent = '📂 フォルダをここへドロップ';
        hint.textContent = 'D&D が難しい場合は参照';
    },

    setupDropZone() {
        const dropZone = document.getElementById('folder-drop-zone');
        if (!dropZone) return;

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });

        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });

        dropZone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');

            const path = await this.extractDroppedPath(e.dataTransfer);
            if (path) {
                document.getElementById('edit-folder').value = path;
                await this.validatePath(path);
            } else {
                UI.log(
                    desktopBridge
                        ? 'D&D から有効なフォルダを取得できませんでした。ネイティブのフォルダ選択を開きます。'
                        : '標準ブラウザの制約で D&D から絶対パスを取得できませんでした。フォルダ参照画面を開きます。',
                    'warning'
                );
                await this.open();
            }
        });

        dropZone.addEventListener('click', () => this.open());
    },

    async extractDroppedPath(dataTransfer) {
        if (!dataTransfer) return '';

        const uriList = dataTransfer.getData('text/uri-list');
        if (uriList) {
            const firstUri = uriList
                .split(/\r?\n/)
                .map(line => line.trim())
                .find(line => line && !line.startsWith('#'));
            const parsed = await this.normalizePathCandidate(this.fileUriToPath(firstUri));
            if (parsed) return parsed;
        }

        const plainText = dataTransfer.getData('text/plain');
        if (plainText) {
            const parsed = this.fileUriToPath(plainText.trim()) || plainText.trim();
            const normalized = await this.normalizePathCandidate(parsed);
            if (normalized) return normalized;
        }

        const items = Array.from(dataTransfer.items || []);
        for (const item of items) {
            if (item.kind !== 'file') continue;
            const file = item.getAsFile ? item.getAsFile() : null;
            const parsed = await this.normalizePathCandidate(await this.getFileSystemPath(file));
            if (parsed) return parsed;
        }

        const files = Array.from(dataTransfer.files || []);
        for (const file of files) {
            const parsed = await this.normalizePathCandidate(await this.getFileSystemPath(file));
            if (parsed) return parsed;
        }

        return '';
    },

    async getFileSystemPath(file) {
        if (!file) {
            return '';
        }

        if (desktopBridge && typeof desktopBridge.getPathForFile === 'function') {
            try {
                const electronPath = await desktopBridge.getPathForFile(file);
                if (electronPath) {
                    return electronPath;
                }
            } catch (error) {
                console.error('getPathForFile error:', error);
            }
        }

        return file.path || '';
    },

    async normalizePathCandidate(pathValue) {
        if (!pathValue) {
            return '';
        }

        if (desktopBridge && typeof desktopBridge.normalizeDroppedPath === 'function') {
            try {
                const normalizedDesktopPath = await desktopBridge.normalizeDroppedPath(pathValue);
                if (normalizedDesktopPath) {
                    return normalizedDesktopPath;
                }
            } catch (error) {
                console.error('normalizeDroppedPath error:', error);
            }
        }

        if (!/^[A-Za-z]:\\/.test(pathValue || '')) {
            return '';
        }

        const normalized = pathValue.trim();
        const lastSegment = normalized.split('\\').pop() || '';
        if (/\.(png|jpg|jpeg|gif|webp|bmp|zip)$/i.test(lastSegment)) {
            return normalized.replace(/\\[^\\]+$/, '');
        }
        return normalized;
    },

    fileUriToPath(uri) {
        if (!uri || !uri.startsWith('file:///')) return '';
        try {
            const decoded = decodeURIComponent(uri.replace('file:///', '')).replace(/\//g, '\\');
            if (/^[A-Za-z]:\\/.test(decoded)) {
                return decoded;
            }
        } catch (error) {
            console.error('fileUriToPath error:', error);
        }
        return '';
    },

    async open() {
        if (desktopBridge && typeof desktopBridge.pickFolder === 'function') {
            const pickedPath = await desktopBridge.pickFolder();
            if (pickedPath) {
                document.getElementById('edit-folder').value = pickedPath;
                await this.validatePath(pickedPath);
            }
            return;
        }

        this.currentPath = '';
        this.selectedPath = '';
        UI.showModal('folder-browser-modal');
        await this.loadFolder('');
    },

    close() {
        UI.hideModal('folder-browser-modal');
    },

    async loadFolder(path) {
        const listContainer = document.getElementById('folder-list');
        listContainer.innerHTML = '<div class="folder-loading">読み込み中...</div>';

        try {
            const data = await API.browseFolders(path);
            this.currentPath = data.path;
            this.updateBreadcrumb(data.path);
            this.renderFolderList(data.items);
            document.getElementById('folder-select-btn').disabled = true;
        } catch (error) {
            listContainer.innerHTML = '<div class="folder-loading">読み込みエラー</div>';
        }
    },

    updateBreadcrumb(path) {
        const container = document.getElementById('folder-breadcrumb');
        container.innerHTML = '<button class="breadcrumb-item" data-path="">💻 ドライブ</button>';

        if (path) {
            const parts = path.split(/[\\\/]/).filter(p => p);
            let currentPath = '';

            parts.forEach((part, index) => {
                if (index === 0 && part.includes(':')) {
                    currentPath = part + '\\';
                } else {
                    currentPath += part + '\\';
                }

                const btn = document.createElement('button');
                btn.className = 'breadcrumb-item';
                btn.dataset.path = currentPath;
                btn.textContent = part;
                btn.addEventListener('click', () => this.loadFolder(currentPath));
                container.appendChild(btn);
            });
        }

        // ドライブボタンのイベント
        container.querySelector('[data-path=""]').addEventListener('click', () => this.loadFolder(''));
    },

    renderFolderList(items) {
        const container = document.getElementById('folder-list');
        container.innerHTML = '';

        if (items.length === 0) {
            container.innerHTML = '<div class="folder-loading">フォルダがありません</div>';
            return;
        }

        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'folder-item';
            div.dataset.path = item.path;
            div.innerHTML = `
                <span class="folder-item-icon">${item.type === 'drive' ? '💽' : '📁'}</span>
                <span class="folder-item-name">${item.name}</span>
            `;

            div.addEventListener('click', () => {
                // 選択状態をトグル
                const isSelected = div.classList.contains('selected');
                container.querySelectorAll('.folder-item').forEach(el => el.classList.remove('selected'));

                if (!isSelected) {
                    div.classList.add('selected');
                    this.selectedPath = item.path;
                    document.getElementById('folder-select-btn').disabled = false;
                } else {
                    this.selectedPath = '';
                    document.getElementById('folder-select-btn').disabled = true;
                }
            });

            div.addEventListener('dblclick', () => {
                this.loadFolder(item.path);
            });

            container.appendChild(div);
        });
    },

    confirmSelection() {
        if (this.selectedPath) {
            document.getElementById('edit-folder').value = this.selectedPath;
            this.validatePath(this.selectedPath);
            this.close();
        }
    },

    async validatePath(path) {
        const validationEl = document.getElementById('folder-validation');
        const iconEl = validationEl.querySelector('.validation-icon');
        const countEl = document.getElementById('image-count');
        const messageEl = document.getElementById('validation-message');

        if (!path) {
            validationEl.classList.add('hidden');
            return;
        }

        try {
            const result = await API.validateFolder(path);
            validationEl.classList.remove('hidden');

            if (result.valid) {
                validationEl.classList.remove('invalid');
                validationEl.classList.toggle('warning', result.image_count === 0);
                iconEl.textContent = result.image_count === 0 ? '⚠️' : '✅';
                messageEl.textContent = result.image_count === 0
                    ? 'フォルダは見つかりましたが、画像がありません。'
                    : 'フォルダを確認しました。画像ファイル:';
                countEl.textContent = result.image_count;
            } else {
                validationEl.classList.add('invalid');
                validationEl.classList.remove('warning');
                iconEl.textContent = '❌';
                messageEl.textContent = 'フォルダが見つかりません。参照ボタンで選び直してください。画像ファイル:';
                countEl.textContent = '0';
            }
        } catch (error) {
            validationEl.classList.remove('hidden');
            validationEl.classList.add('invalid');
            validationEl.classList.remove('warning');
            iconEl.textContent = '❌';
            messageEl.textContent = 'フォルダ確認に失敗しました。パスを見直すか、参照ボタンを使ってください。画像ファイル:';
            countEl.textContent = '0';
        }
    }
};

// ==============================
// 初期化
// ==============================

document.addEventListener('DOMContentLoaded', () => {
    try {
        UI.init();
    } catch (error) {
        console.error('UI init failed:', error);
    }
    try {
        FolderBrowser.init();
    } catch (error) {
        console.error('FolderBrowser init failed:', error);
    }
});
