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
    seenProcessEvents: new Set()
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
            stopProcessBtn: document.getElementById('stop-process-btn'),
            actionButtons: Array.from(document.querySelectorAll('.btn-action')),
            runAllBtn: document.getElementById('run-all-btn'),
            refreshBtn: document.getElementById('refresh-btn'),
            addTaskBtn: document.getElementById('add-task-btn'),
            saveSettingsBtn: document.getElementById('save-settings-btn'),
            editTaskModal: document.getElementById('edit-task-modal'),
            editTaskForm: document.getElementById('edit-task-form'),
            settingsForm: document.getElementById('settings-form')
        };

        // イベントリスナー設定
        this.setupEventListeners();

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
        this.elements.refreshBtn.addEventListener('click', () => {
            this.loadTasks();
        });

        // タスク追加ボタン
        this.elements.addTaskBtn.addEventListener('click', () => {
            if (state.isProcessing) {
                this.log('処理中はタスク追加できません。完了後に再度お試しください。', 'warning');
                return;
            }
            this.openEditModal(-1); // -1 = 新規作成
        });

        // モーダル閉じる
        document.querySelectorAll('.modal-close, .modal-cancel, .modal-overlay').forEach(el => {
            el.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-overlay') ||
                    e.target.classList.contains('modal-close') ||
                    e.target.classList.contains('modal-cancel')) {
                    this.hideModal('edit-task-modal');
                }
            });
        });

        // タスク編集フォーム
        this.elements.editTaskForm.addEventListener('submit', async (e) => {
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
        this.elements.runAllBtn.addEventListener('click', async () => {
            await this.runAllSteps();
        });

        this.elements.stopProcessBtn.addEventListener('click', async () => {
            await this.stopCurrentProcess();
        });

        // ログクリア
        document.getElementById('clear-log-btn').addEventListener('click', () => {
            this.elements.logContainer.innerHTML = '';
            this.log('ログをクリアしました', 'info');
        });

        // 設定保存
        this.elements.saveSettingsBtn.addEventListener('click', async () => {
            if (state.isProcessing) {
                this.log('処理中は設定保存できません。完了後に再度お試しください。', 'warning');
                return;
            }
            await this.handleSaveSettings();
        });
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
    },

    // 編集モーダルを開く
    openEditModal(index) {
        if (this.isTaskMutationLocked()) {
            this.log('処理中はタスク編集できません。完了後に再度お試しください。', 'warning');
            return;
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
                            const [h, m] = timePart.split(':').map(Number);
                            let roundedMin = m < 15 ? 0 : m < 45 ? 30 : 0;
                            let roundedHour = m >= 45 ? (h + 1) % 24 : h;
                            scheduleTimeInput.value = `${String(roundedHour).padStart(2, '0')}:${String(roundedMin).padStart(2, '0')}`;
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
            return;
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
        } catch (error) {
            this.log(`${stepNames[step]} に失敗しました: ${error.message}`, 'error');
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

        for (const step of steps) {
            await this.runStep(step);
            if (state.runtime.execution.active) {
                this.log('別処理が継続中のため、全ステップ実行を中断します。', 'warning');
                break;
            }
            completed++;
            this.showProgress((completed / steps.length) * 100);
        }

        if (!state.runtime.execution.active) {
            this.log('前処理まとめ実行が完了しました', 'success');
            state.isProcessing = false;
        }
    },

    async checkConnection() {
        try {
            const status = await API.getStatus();
            this.setConnectionStatus(true);
            if (status.runtime) {
                this.applyRuntimeState(status.runtime);
            }
        } catch {
            this.setConnectionStatus(false);
            this.log('サーバーに接続できません。再読み込みするか、起動バッチを確認してください。', 'warning');
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
            this.applyRuntimeState(runtime);
        } catch (error) {
            this.setConnectionStatus(false);
            this.log('接続が切れました。処理中なら待機し、復旧しない場合は起動バッチを確認してください。', 'warning');
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
        const stopBtn = this.elements.stopProcessBtn;

        if (!execution.active) {
            box.classList.add('hidden');
            box.classList.remove('is-busy');
            box.classList.remove('is-warning');
            box.classList.remove('is-error');
            stopBtn.classList.add('hidden');
            text.textContent = '待機中';
            this.highlightActiveStep('');
            return;
        }

        box.classList.remove('hidden');
        box.classList.add('is-busy');
        box.classList.toggle('is-warning', execution.message_level === 'warning');
        box.classList.toggle('is-error', execution.message_level === 'error');
        const elapsed = execution.elapsed_seconds ? ` (${Math.floor(execution.elapsed_seconds)}s)` : '';
        text.textContent = (execution.message || `${execution.step} を実行中です。`) + elapsed;

        if (execution.kind === 'browser_process' && execution.process_id) {
            stopBtn.classList.remove('hidden');
        } else {
            stopBtn.classList.add('hidden');
        }

        this.highlightActiveStep(execution.step || '');
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
        this.elements.actionButtons.forEach(btn => {
            btn.disabled = disabled;
        });
        this.elements.runAllBtn.disabled = disabled;
        this.refreshActionLockState();
    },

    refreshActionLockState() {
        const taskLocked = this.isTaskMutationLocked();
        this.elements.addTaskBtn.disabled = taskLocked;
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
        document.getElementById(id).classList.remove('hidden');
    },

    hideModal(id) {
        document.getElementById(id).classList.add('hidden');
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
        if (!hint) return;

        if (desktopBridge && typeof desktopBridge.pickFolder === 'function') {
            hint.textContent = 'Electron では参照ボタンからネイティブ選択が使えます。D&D は補助として使えます。';
            return;
        }

        hint.textContent = '標準ブラウザでは D&D から絶対パスを取得できない場合があります。参照ボタンを優先してください。';
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

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');

            const path = this.extractDroppedPath(e.dataTransfer);
            if (path) {
                document.getElementById('edit-folder').value = path;
                this.validatePath(path);
            } else {
                UI.log(
                    desktopBridge
                        ? 'D&D からパスを取得できませんでした。ネイティブのフォルダ選択を開きます。'
                        : '標準ブラウザの制約で D&D から絶対パスを取得できませんでした。フォルダ参照画面を開きます。',
                    'warning'
                );
                this.open();
            }
        });

        dropZone.addEventListener('click', () => this.open());
    },

    extractDroppedPath(dataTransfer) {
        if (!dataTransfer) return '';

        const uriList = dataTransfer.getData('text/uri-list');
        if (uriList) {
            const firstUri = uriList
                .split(/\r?\n/)
                .map(line => line.trim())
                .find(line => line && !line.startsWith('#'));
            const parsed = this.fileUriToPath(firstUri);
            if (parsed) return parsed;
        }

        const plainText = dataTransfer.getData('text/plain');
        if (plainText) {
            const parsed = this.fileUriToPath(plainText.trim()) || plainText.trim();
            if (/^[A-Za-z]:\\/.test(parsed)) return parsed;
        }

        const items = Array.from(dataTransfer.items || []);
        for (const item of items) {
            if (item.kind !== 'file') continue;
            const file = item.getAsFile ? item.getAsFile() : null;
            const parsed = this.normalizeDroppedPath(file && file.path ? file.path : '');
            if (parsed) return parsed;
        }

        const files = Array.from(dataTransfer.files || []);
        for (const file of files) {
            const parsed = this.normalizeDroppedPath(file.path || '');
            if (parsed) return parsed;
        }

        return '';
    },

    normalizeDroppedPath(pathValue) {
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
    UI.init();
    FolderBrowser.init();
});
