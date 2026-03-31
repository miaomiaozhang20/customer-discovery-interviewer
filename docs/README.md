# Customer Discovery Interviewer - Web App

This is the static web version of the Customer Discovery Interviewer, designed to run entirely in your browser on GitHub Pages.

## 🌐 Live Demo

Access the live app at: **https://miaomiaozhang20.github.io/customer-discovery-interviewer/**

## ✨ Features

- **100% Client-Side**: Runs entirely in your browser, no server needed
- **Two-Stage Process**: Interview → Insights Report
- **AI-Powered**: Uses Anthropic Claude or OpenAI GPT
- **Privacy First**: API keys stored locally, never sent to any server
- **Export Reports**: Download as Word document
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
2. Start chatting with the AI interviewer
3. Answer questions about your experiences and challenges
4. The AI will ask three required questions at the end:
   - Would you be willing to pay?
   - What questions am I missing?
   - Can we contact you? (email)

### 4. Generate Report

1. Click "Start Report Writer"
2. The AI generates a comprehensive insights report
3. Request changes or refinements as needed
4. Download the final report as a Word document

## 🔒 Privacy & Security

- **Your API key is stored locally** in your browser's localStorage
- **No data is sent to any server** except directly to your chosen AI provider (Anthropic or OpenAI)
- **Sessions are saved locally** to your device only
- **No tracking or analytics** - completely private

## 💾 Session Management

- **Save Session**: Download your interview as a JSON file
- **Load Session**: Upload a previously saved session to continue
- **Export Transcript**: Download the full conversation as text
- **Export Report**: Download insights report as Word document

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
