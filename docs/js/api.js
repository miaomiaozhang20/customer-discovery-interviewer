// API Handler for AI providers
class AIProvider {
    constructor() {
        this.provider = localStorage.getItem('ai_provider') || CONFIG.DEFAULTS.provider;
        this.model = localStorage.getItem('ai_model') || CONFIG.DEFAULTS.model;
        this.temperature = parseFloat(localStorage.getItem('ai_temperature')) || CONFIG.DEFAULTS.temperature;
    }

    getApiKey() {
        if (this.provider === 'anthropic') {
            return localStorage.getItem('anthropic_api_key');
        } else if (this.provider === 'openai') {
            return localStorage.getItem('openai_api_key');
        }
        return null;
    }

    async sendMessage(messages, systemPrompt, options = {}) {
        const apiKey = this.getApiKey();
        if (!apiKey) {
            throw new Error('API key not configured. Please add your API key in Settings.');
        }

        if (this.provider === 'anthropic') {
            return await this.callAnthropic(messages, systemPrompt, apiKey, options);
        } else if (this.provider === 'openai') {
            return await this.callOpenAI(messages, systemPrompt, apiKey, options);
        }

        throw new Error('Unsupported AI provider');
    }

    async callAnthropic(messages, systemPrompt, apiKey, options) {
        const url = 'https://api.anthropic.com/v1/messages';

        const body = {
            model: this.model,
            max_tokens: options.maxTokens || CONFIG.DEFAULTS.maxTokens,
            temperature: options.temperature || this.temperature,
            system: systemPrompt,
            messages: messages.map(msg => ({
                role: msg.role === 'ai' ? 'assistant' : msg.role,
                content: msg.content
            }))
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-api-key': apiKey,
                    'anthropic-version': '2023-06-01'
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || `API error: ${response.status}`);
            }

            const data = await response.json();
            return data.content[0].text;

        } catch (error) {
            console.error('Anthropic API error:', error);
            throw error;
        }
    }

    async callOpenAI(messages, systemPrompt, apiKey, options) {
        const url = 'https://api.openai.com/v1/chat/completions';

        const body = {
            model: this.model,
            temperature: options.temperature || this.temperature,
            max_tokens: options.maxTokens || CONFIG.DEFAULTS.maxTokens,
            messages: [
                { role: 'system', content: systemPrompt },
                ...messages.map(msg => ({
                    role: msg.role === 'ai' ? 'assistant' : msg.role,
                    content: msg.content
                }))
            ]
        };

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`
                },
                body: JSON.stringify(body)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error?.message || `API error: ${response.status}`);
            }

            const data = await response.json();
            return data.choices[0].message.content;

        } catch (error) {
            console.error('OpenAI API error:', error);
            throw error;
        }
    }

    updateSettings(provider, model, temperature) {
        this.provider = provider;
        this.model = model;
        this.temperature = temperature;

        localStorage.setItem('ai_provider', provider);
        localStorage.setItem('ai_model', model);
        localStorage.setItem('ai_temperature', temperature.toString());
    }

    setApiKey(provider, apiKey) {
        if (provider === 'anthropic') {
            localStorage.setItem('anthropic_api_key', apiKey);
        } else if (provider === 'openai') {
            localStorage.setItem('openai_api_key', apiKey);
        }
    }
}

// Global API instance
const api = new AIProvider();
