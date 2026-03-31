// UI Manager
class UIManager {
    constructor() {
        this.messagesContainer = document.getElementById('messagesContainer');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        this.instructionsPanel = document.getElementById('instructionsPanel');
    }

    init() {
        this.loadMessages();
        this.updateStageUI();
        this.loadSettings();
    }

    addMessage(role, content, timestamp = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'ai' ? '🎯' : '👤';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        bubble.innerHTML = this.formatMarkdown(content);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = timestamp
            ? new Date(timestamp).toLocaleTimeString()
            : new Date().toLocaleTimeString();

        contentDiv.appendChild(bubble);
        contentDiv.appendChild(time);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(contentDiv);

        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();

        return messageDiv;
    }

    loadMessages() {
        this.messagesContainer.innerHTML = '';
        const messages = storage.getMessages();

        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content, msg.timestamp);
        });

        if (messages.length === 0) {
            this.showInstructions();
        }
    }

    showInstructions() {
        const stage = storage.getStage();
        const instructions = stage === 'interview'
            ? CONFIG.INSTRUCTIONS.INTERVIEW
            : CONFIG.INSTRUCTIONS.REPORT;

        const content = document.getElementById('instructionsContent');
        content.innerHTML = this.formatMarkdown(instructions);
        this.instructionsPanel.style.display = 'block';
    }

    hideInstructions() {
        this.instructionsPanel.style.display = 'none';
    }

    formatMarkdown(text) {
        let html = text;

        // Headers
        html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
        html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
        html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

        // Blockquotes
        html = html.replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>');

        // Bold
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

        // Italic
        html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Links
        html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');

        // Unordered lists
        html = html.replace(/^\* (.*$)/gim, '<li>$1</li>');
        html = html.replace(/^- (.*$)/gim, '<li>$1</li>');

        // Numbered lists
        html = html.replace(/^\d+\. (.*$)/gim, '<li>$1</li>');

        // Wrap consecutive list items in ul/ol
        html = html.replace(/(<li>.*<\/li>\n?)+/gim, match => `<ul>${match}</ul>`);

        // Code blocks
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // Line breaks
        html = html.replace(/\n/g, '<br>');

        return html;
    }

    clearInput() {
        this.userInput.value = '';
        this.userInput.style.height = 'auto';
    }

    showLoading() {
        this.loadingIndicator.style.display = 'flex';
        this.sendBtn.disabled = true;
    }

    hideLoading() {
        this.loadingIndicator.style.display = 'none';
        this.sendBtn.disabled = false;
    }

    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }

    showError(message) {
        alert(`Error: ${message}`);
    }

    showSuccess(message) {
        // Create temporary success notification
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10B981;
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            z-index: 1000;
            animation: fadeIn 0.3s;
        `;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'fadeOut 0.3s';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    updateStageUI() {
        const stage = storage.getStage();

        // Update stage indicators
        const interviewStage = document.getElementById('stageInterview');
        const reportStage = document.getElementById('stageReport');

        if (stage === 'interview') {
            interviewStage.classList.add('active');
            reportStage.classList.remove('active');
            document.getElementById('switchStageBtn').textContent = 'Start Report Writer';
            document.getElementById('exportReportBtn').disabled = true;
        } else {
            interviewStage.classList.remove('active');
            reportStage.classList.add('active');
            document.getElementById('switchStageBtn').textContent = 'Return to Interview';
            document.getElementById('exportReportBtn').disabled = false;
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
    }

    loadSettings() {
        const provider = localStorage.getItem('ai_provider') || CONFIG.DEFAULTS.provider;
        const model = localStorage.getItem('ai_model') || CONFIG.DEFAULTS.model;
        const temperature = localStorage.getItem('ai_temperature') || CONFIG.DEFAULTS.temperature;
        const anthropicKey = localStorage.getItem('anthropic_api_key') || '';
        const openaiKey = localStorage.getItem('openai_api_key') || '';

        document.getElementById('apiProvider').value = provider;
        document.getElementById('modelSelect').value = model;
        document.getElementById('temperature').value = temperature;
        document.getElementById('temperatureValue').textContent = temperature;
        document.getElementById('anthropicKey').value = anthropicKey;
        document.getElementById('openaiKey').value = openaiKey;

        this.toggleApiKeyInputs(provider);
    }

    toggleApiKeyInputs(provider) {
        const anthropicGroup = document.getElementById('anthropicKeyGroup');
        const openaiGroup = document.getElementById('openaiKeyGroup');

        if (provider === 'anthropic') {
            anthropicGroup.style.display = 'block';
            openaiGroup.style.display = 'none';
        } else {
            anthropicGroup.style.display = 'none';
            openaiGroup.style.display = 'block';
        }
    }

    async loadProductFile(file) {
        if (file.type === 'application/pdf') {
            this.showError('PDF parsing not yet implemented. Please paste text instead.');
            return;
        }

        const text = await file.text();
        document.getElementById('productDescription').value = text;
        storage.setProductDescription(text);
        this.showSuccess('Product description loaded');
    }

    async loadSessionFile(file) {
        try {
            await storage.loadSessionFromFile(file);
            this.loadMessages();
            this.updateStageUI();
            this.showSuccess('Session loaded successfully');
        } catch (error) {
            this.showError(error.message);
        }
    }
}

// Global UI instance
const ui = new UIManager();
