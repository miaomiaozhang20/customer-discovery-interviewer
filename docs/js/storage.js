// Storage Manager for sessions
class StorageManager {
    constructor() {
        this.currentSession = this.loadCurrentSession();
    }

    loadCurrentSession() {
        const saved = localStorage.getItem('current_session');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch (e) {
                console.error('Error loading session:', e);
            }
        }

        return this.createNewSession();
    }

    createNewSession() {
        return {
            id: this.generateId(),
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            stage: 'interview', // 'interview' or 'report'
            productDescription: '',
            messages: [],
            requiredQuestionsAsked: {
                willingness_to_pay: false,
                missing_questions: false,
                contact_permission: false
            },
            report: null
        };
    }

    generateId() {
        return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    }

    saveCurrentSession() {
        this.currentSession.updatedAt = new Date().toISOString();
        localStorage.setItem('current_session', JSON.stringify(this.currentSession));
    }

    addMessage(role, content) {
        const message = {
            id: this.generateId(),
            role: role, // 'user' or 'ai'
            content: content,
            timestamp: new Date().toISOString()
        };

        this.currentSession.messages.push(message);
        this.saveCurrentSession();
        return message;
    }

    getMessages() {
        return this.currentSession.messages;
    }

    getMessagesForAPI() {
        return this.currentSession.messages.map(msg => ({
            role: msg.role === 'ai' ? 'assistant' : 'user',
            content: msg.content
        }));
    }

    setStage(stage) {
        this.currentSession.stage = stage;
        this.saveCurrentSession();
    }

    getStage() {
        return this.currentSession.stage;
    }

    setProductDescription(description) {
        this.currentSession.productDescription = description;
        this.saveCurrentSession();
    }

    getProductDescription() {
        return this.currentSession.productDescription;
    }

    markQuestionAsked(questionId) {
        this.currentSession.requiredQuestionsAsked[questionId] = true;
        this.saveCurrentSession();
    }

    areAllQuestionsAsked() {
        return Object.values(this.currentSession.requiredQuestionsAsked).every(v => v === true);
    }

    setReport(report) {
        this.currentSession.report = report;
        this.saveCurrentSession();
    }

    getReport() {
        return this.currentSession.report;
    }

    exportSession() {
        const data = JSON.stringify(this.currentSession, null, 2);
        const blob = new Blob([data], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interview_${this.currentSession.id}_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    exportTranscript() {
        let transcript = `Customer Discovery Interview\n`;
        transcript += `Date: ${new Date(this.currentSession.createdAt).toLocaleString()}\n`;
        transcript += `Session ID: ${this.currentSession.id}\n`;
        transcript += `\n${'='.repeat(60)}\n\n`;

        if (this.currentSession.productDescription) {
            transcript += `Product/Service Description:\n${this.currentSession.productDescription}\n\n`;
            transcript += `${'='.repeat(60)}\n\n`;
        }

        this.currentSession.messages.forEach((msg, index) => {
            const role = msg.role === 'ai' ? 'Interviewer' : 'Interviewee';
            const time = new Date(msg.timestamp).toLocaleTimeString();
            transcript += `[${time}] ${role}:\n${msg.content}\n\n`;
        });

        const blob = new Blob([transcript], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `transcript_${this.currentSession.id}_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }

    loadSessionFromFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
                try {
                    const session = JSON.parse(e.target.result);
                    this.currentSession = session;
                    this.saveCurrentSession();
                    resolve(session);
                } catch (error) {
                    reject(new Error('Invalid session file'));
                }
            };
            reader.onerror = () => reject(new Error('Failed to read file'));
            reader.readAsText(file);
        });
    }

    resetSession() {
        this.currentSession = this.createNewSession();
        this.saveCurrentSession();
    }

    getSessionHistory() {
        // In a more advanced version, this could store multiple sessions
        // For now, we only have the current session
        return [this.currentSession];
    }
}

// Global storage instance
const storage = new StorageManager();
