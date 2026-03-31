// Interviewer Agent
class Interviewer {
    constructor() {
        this.systemPrompt = SYSTEM_PROMPTS.INTERVIEWER;
        this.questionCounter = 0;
    }

    getInitialMessage() {
        const productDesc = storage.getProductDescription();
        let message = "Hi! Thank you for taking the time to speak with me today. I'm here to learn about your experiences and challenges";

        if (productDesc) {
            message += " related to the product/service we'll be discussing";
        }

        message += ". This conversation will help us understand if and how we might be able to help people like you. There are no right or wrong answers—I'm just here to listen and learn from your experiences.\n\nTo start, could you tell me a bit about yourself and your current situation?";

        return message;
    }

    async sendMessage(userMessage) {
        try {
            // Add user message to storage
            storage.addMessage('user', userMessage);

            // Check if we need to ask required questions
            const shouldAskRequired = this.shouldAskRequiredQuestions();

            // Prepare messages for API
            let messages = storage.getMessagesForAPI();

            // Add context about product if available
            let contextualPrompt = this.systemPrompt;
            const productDesc = storage.getProductDescription();
            if (productDesc) {
                contextualPrompt += `\n\nProduct/Service being discussed:\n${productDesc}`;
            }

            // Add reminder about required questions if needed
            if (shouldAskRequired) {
                contextualPrompt += `\n\nIMPORTANT: The interview is well underway. After addressing the current topic, you MUST ask the three required questions in order:
1. "Would you be willing to pay for [product/service]?"
2. "What question(s) should I be asking that I haven't included?"
3. "Are you willing to be contacted by founders, which will entail sharing of your contact information? If yes, please leave your email address here."

Ask these questions one at a time, not all at once.`;
            }

            // Get AI response
            const response = await api.sendMessage(messages, contextualPrompt);

            // Check if response contains required questions
            this.detectRequiredQuestions(response);

            // Add AI response to storage
            storage.addMessage('ai', response);

            return response;

        } catch (error) {
            console.error('Interviewer error:', error);
            throw error;
        }
    }

    shouldAskRequiredQuestions() {
        const messages = storage.getMessages();
        const allAsked = storage.areAllQuestionsAsked();

        // Ask required questions after at least 10 messages and not all asked yet
        return messages.length >= 10 && !allAsked;
    }

    detectRequiredQuestions(response) {
        const lower = response.toLowerCase();

        // Check for willingness to pay question
        if (lower.includes('willing to pay') || lower.includes('would you pay')) {
            storage.markQuestionAsked('willingness_to_pay');
        }

        // Check for missing questions question
        if (lower.includes('what question') && lower.includes('haven\'t included')) {
            storage.markQuestionAsked('missing_questions');
        }

        // Check for contact permission question
        if (lower.includes('willing to be contacted') ||
            (lower.includes('contact') && lower.includes('email'))) {
            storage.markQuestionAsked('contact_permission');
        }
    }

    async handleSkip() {
        const message = "I understand you'd prefer not to discuss this topic. Let's move on. Is there another aspect of your experience you'd like to explore?";
        storage.addMessage('ai', message);
        return message;
    }

    getProgress() {
        const questions = storage.currentSession.requiredQuestionsAsked;
        const total = Object.keys(questions).length;
        const asked = Object.values(questions).filter(v => v).length;
        return { asked, total };
    }
}

// Global interviewer instance
const interviewer = new Interviewer();
