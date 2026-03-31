# Customer Discovery Interviewer - Web App

This is the static web version of the Customer Discovery Interviewer, designed to run entirely in your browser on GitHub Pages.

## 🌐 Live Demo

Access the live app at: **https://miaomiaozhang20.github.io/customer-discovery-interviewer/**

## ✨ Features

- **100% Client-Side**: Runs entirely in your browser, no server needed
- **AI-Powered Interview**: Uses Anthropic Claude or OpenAI GPT for conversational interviews
- **Daily Problems Focus**: Starts by asking about problems you try to solve in daily life
- **Three Required Questions**: Automatically asks about willingness to pay, missing questions, and contact permission
- **Privacy First**: API keys stored locally, never sent to any server
- **Export Transcripts**: Download full interview as text file
- **Session Management**: Save and load interview sessions
- **Responsive Design**: Works on desktop and mobile

## 🚀 How to Use

### 1. Get Your API Key

You need an API key from either:
- **Anthropic Claude**: https://console.anthropic.com/ (Recommended)
- **OpenAI**: https://platform.openai.com/

### 2. Configure Settings

1. Click the ⚙️ Settings icon
2. Select your AI provider
3. Paste your API key
4. Choose your model and temperature
5. Click "Save Settings"

### 3. Conduct Interview

1. Optionally upload or paste a product description
2. The AI will start by asking: **"What are some problems you try to solve in your daily life?"**
3. Answer questions about your experiences and challenges
4. The AI will probe deeper with follow-up questions
5. At the end, the AI will ask three required questions:
   - Would you be willing to pay for [product]?
   - What questions should I be asking that I haven't included?
   - Are you willing to be contacted by founders? (If yes, provide email)

### 4. Export Your Interview

1. Click "Export Transcript" to download the full conversation
2. The transcript includes all questions and answers
3. Use it for analysis, sharing with team, or your records

## 🔒 Privacy & Security

- **Your API key is stored locally** in your browser's localStorage
- **No data is sent to any server** except directly to your chosen AI provider (Anthropic or OpenAI)
- **Sessions are saved locally** to your device only
- **No tracking or analytics** - completely private

## 💾 Session Management

- **Save Session**: Download your interview as a JSON file
- **Load Session**: Upload a previously saved session to continue
- **Export Transcript**: Download the full conversation as text file
- **New Interview**: Start a fresh interview (saves your progress automatically)

## 🎯 What Makes a Good Interview

### Green Flags (Look For)
- Specific, recent examples
- Current spending on the problem
- Emotional responses when describing pain
- Concrete use cases
- Willingness to pay with amounts
- Sharing contact information

### Red Flags (Watch Out)
- Vague or hypothetical responses
- Polite enthusiasm without specifics
- No current pain point
- Unwilling to pay
- Answering on behalf of others

## 🛠️ Technical Details

### Built With
- Pure HTML5, CSS3, JavaScript (ES6+)
- No frameworks or build tools
- localStorage for persistence
- Fetch API for AI provider calls

### Browser Support
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome)

### API Providers
- **Anthropic Claude API**: claude-3-7-sonnet, claude-3-5-sonnet
- **OpenAI API**: gpt-4o, gpt-4o-mini

## 📱 Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Esc**: Clear input field

## ❓ Troubleshooting

### "API key required"
Add your API key in Settings (⚙️ icon)

### "API error: 401"
Your API key is invalid or expired. Check your API key.

### "API error: 429"
You've hit rate limits. Wait a moment and try again.

### Messages not sending
1. Check your internet connection
2. Verify your API key is correct
3. Check browser console for errors (F12)

### Report won't generate
Ensure you have at least 4-5 message exchanges in the interview

## 🐛 Report Issues

Found a bug? [Report it on GitHub](https://github.com/miaomiaozhang20/customer-discovery-interviewer/issues)

## 📖 Methodology

Based on proven customer discovery frameworks:
- **The Mom Test** by Rob Fitzpatrick
- **Lean Customer Development** by Cindy Alvarez
- **Jobs to Be Done** framework
- Y Combinator startup advice

## 📄 License

See main repository for license information.

---

**Built to help founders discover the truth about their ideas.** 🎯
