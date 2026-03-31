// Main Application
class App {
    constructor() {
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;

        // Initialize UI
        ui.init();

        // Setup event listeners
        this.setupEventListeners();

        // Start interview if no messages
        if (storage.getMessages().length === 0) {
            this.startInterview();
        }

        this.initialized = true;
        console.log('App initialized');
    }

    setupEventListeners() {
        // Send message
        document.getElementById('sendBtn').addEventListener('click', () => this.handleSend());
        document.getElementById('userInput').addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.handleSend();
            }
        });

        // Skip question
        document.getElementById('skipBtn').addEventListener('click', () => this.handleSkip());

        // Session management
        document.getElementById('newSessionBtn').addEventListener('click', () => this.handleNewSession());
        document.getElementById('saveSessionBtn').addEventListener('click', () => storage.exportSession());
        document.getElementById('loadSessionBtn').addEventListener('click', () => {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = '.json';
            input.onchange = (e) => ui.loadSessionFile(e.target.files[0]);
            input.click();
        });

        // Stage switching
        document.getElementById('switchStageBtn').addEventListener('click', () => this.handleStageSwitch());

        // Export
        document.getElementById('exportReportBtn').addEventListener('click', () => this.handleExportReport());
        document.getElementById('exportTranscriptBtn').addEventListener('click', () => storage.exportTranscript());

        // Product upload
        document.getElementById('uploadProductBtn').addEventListener('click', () => {
            document.getElementById('productFile').click();
        });
        document.getElementById('productFile').addEventListener('change', (e) => {
            if (e.target.files[0]) {
                ui.loadProductFile(e.target.files[0]);
            }
        });
        document.getElementById('productDescription').addEventListener('change', (e) => {
            storage.setProductDescription(e.target.value);
        });

        // Settings
        document.getElementById('settingsBtn').addEventListener('click', () => {
            ui.showModal('settingsModal');
        });
        document.getElementById('closeSettings').addEventListener('click', () => {
            ui.hideModal('settingsModal');
        });
        document.getElementById('saveSettings').addEventListener('click', () => this.handleSaveSettings());

        // API provider change
        document.getElementById('apiProvider').addEventListener('change', (e) => {
            ui.toggleApiKeyInputs(e.target.value);
        });

        // Temperature slider
        document.getElementById('temperature').addEventListener('input', (e) => {
            document.getElementById('temperatureValue').textContent = e.target.value;
        });

        // Help
        document.getElementById('helpBtn').addEventListener('click', () => {
            document.getElementById('helpContent').innerHTML = ui.formatMarkdown(CONFIG.HELP);
            ui.showModal('helpModal');
        });
        document.getElementById('closeHelp').addEventListener('click', () => {
            ui.hideModal('helpModal');
        });

        // Instructions
        document.getElementById('closeInstructions').addEventListener('click', () => {
            ui.hideInstructions();
        });

        // Close modals on outside click
        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                e.target.classList.remove('show');
            }
        });
    }

    async startInterview() {
        const initialMessage = interviewer.getInitialMessage();
        storage.addMessage('ai', initialMessage);
        ui.addMessage('ai', initialMessage);
    }

    async handleSend() {
        const message = ui.userInput.value.trim();
        if (!message) return;

        // Check if API key is configured
        if (!api.getApiKey()) {
            ui.showError('Please configure your API key in Settings first.');
            ui.showModal('settingsModal');
            return;
        }

        // Add user message to UI
        ui.addMessage('user', message);
        ui.clearInput();
        ui.showLoading();

        try {
            const stage = storage.getStage();

            if (stage === 'interview') {
                // Interview stage
                const response = await interviewer.sendMessage(message);
                ui.addMessage('ai', response);

                // Check if all required questions are asked
                if (storage.areAllQuestionsAsked()) {
                    setTimeout(() => {
                        const msg = "Thank you so much for your time and for sharing your experiences so openly. Your insights are incredibly valuable and will help us make better decisions about how to move forward.\n\nYou can click the 'Start Report Writer' button on the left-hand sidebar to generate an insights report from our conversation.";
                        storage.addMessage('ai', msg);
                        ui.addMessage('ai', msg);
                    }, 1000);
                }

            } else {
                // Report stage
                if (!storage.getReport()) {
                    ui.showError('Please generate the initial report first.');
                } else {
                    const refinedReport = await reportWriter.refineReport(message);
                    ui.addMessage('ai', refinedReport);
                }
            }

        } catch (error) {
            ui.showError(error.message);
            console.error('Send error:', error);
        } finally {
            ui.hideLoading();
        }
    }

    async handleSkip() {
        const stage = storage.getStage();

        if (stage === 'interview') {
            const response = await interviewer.handleSkip();
            ui.addMessage('ai', response);
        }
    }

    handleNewSession() {
        if (confirm('Are you sure you want to start a new interview? Current session will be lost unless you save it.')) {
            storage.resetSession();
            ui.loadMessages();
            ui.updateStageUI();
            this.startInterview();
        }
    }

    async handleStageSwitch() {
        const currentStage = storage.getStage();

        if (currentStage === 'interview') {
            // Switch to report
            if (storage.getMessages().length < 4) {
                ui.showError('Please conduct a longer interview before generating a report.');
                return;
            }

            if (!storage.areAllQuestionsAsked()) {
                if (!confirm('Not all required questions have been asked. Generate report anyway?')) {
                    return;
                }
            }

            if (confirm('Switch to Report Writer? This will preserve your interview conversation.')) {
                storage.setStage('report');
                ui.updateStageUI();
                ui.showLoading();

                try {
                    const report = await reportWriter.generateInitialReport();
                    ui.loadMessages(); // Reload to show report
                    ui.showSuccess('Report generated! You can now request changes.');
                } catch (error) {
                    ui.showError(error.message);
                    storage.setStage('interview');
                    ui.updateStageUI();
                } finally {
                    ui.hideLoading();
                }
            }

        } else {
            // Switch back to interview
            if (confirm('Return to Interviewer? Your current Report Writer chat history will be cleared.')) {
                storage.setStage('interview');
                ui.updateStageUI();
                ui.loadMessages();
                ui.showSuccess('Returned to interview stage');
            }
        }
    }

    handleExportReport() {
        try {
            reportWriter.exportReportAsWord();
            ui.showSuccess('Report exported successfully');
        } catch (error) {
            ui.showError(error.message);
        }
    }

    handleSaveSettings() {
        const provider = document.getElementById('apiProvider').value;
        const model = document.getElementById('modelSelect').value;
        const temperature = parseFloat(document.getElementById('temperature').value);

        // Save API keys
        if (provider === 'anthropic') {
            const key = document.getElementById('anthropicKey').value.trim();
            if (key) {
                api.setApiKey('anthropic', key);
            }
        } else if (provider === 'openai') {
            const key = document.getElementById('openaiKey').value.trim();
            if (key) {
                api.setApiKey('openai', key);
            }
        }

        // Update API settings
        api.updateSettings(provider, model, temperature);

        ui.hideModal('settingsModal');
        ui.showSuccess('Settings saved successfully');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const app = new App();
    app.init();
});
