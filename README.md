# Customer Discovery Interviewer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://customer-discovery-interviewer.streamlit.app)
[![GitHub](https://img.shields.io/github/stars/miaomiaozhang20/customer-discovery-interviewer?style=social)](https://github.com/miaomiaozhang20/customer-discovery-interviewer)

An AI-powered interview system designed to help founders and product teams conduct effective customer discovery interviews for market validation and demand discovery.

## 🚀 Try It Live

**🌐 Web App (GitHub Pages)**: https://miaomiaozhang20.github.io/customer-discovery-interviewer/

**No installation required!** Just visit the link, add your API key, and start interviewing.

### Two Versions Available:

1. **Web Version (Recommended for Quick Start)**
   - Runs 100% in your browser
   - No installation needed
   - Works on any device
   - Privacy-first (data stays local)
   - [Try it now →](https://miaomiaozhang20.github.io/customer-discovery-interviewer/)

2. **Python/Streamlit Version (For Self-Hosting)**
   - Run on your own server
   - More control over deployment
   - See [DEPLOYMENT.md](DEPLOYMENT.md) for instructions

## Overview

This tool helps entrepreneurs avoid building products nobody wants by conducting rigorous customer discovery interviews. It's based on proven methodologies including The Mom Test, Lean Customer Development, and Jobs to Be Done frameworks.

## Key Features

### 🎯 Two-Stage Interview Process

**Stage 1: Customer Interview**
- Guided conversation exploring problems, needs, and behaviors
- Probing questions that dig deep into specific examples
- Focus on past behavior, not future intentions
- Three required questions at the end:
  1. "Would you be willing to pay for [product/service]?"
  2. "What question(s) should I be asking that I haven't included?"
  3. "Are you willing to be contacted by founders? (If yes, leave your email)"

**Stage 2: Insights Report**
- Transforms interview into structured insights report
- Analyzes validation signals (green flags) and warning signs (red flags)
- Provides actionable recommendations
- Distinguishes genuine interest from polite enthusiasm
- Includes willingness to pay analysis

### 🧠 Intelligent AI Agents

The system uses two specialized AI agents (see [agents.md](agents.md) for full details):

1. **Customer Interviewer Agent**: Skilled at drawing out genuine pain points and behaviors through adaptive probing questions
2. **Insights Report Writer Agent**: Analyzes conversations objectively to provide actionable insights

### ✅ Validation-Focused

The interviewer helps identify:
- **Green Flags**: Specific problems, current spending, emotional responses, willingness to pay
- **Red Flags**: Vague enthusiasm, hypothetical responses, no pain point, unwillingness to pay

## Setup

### Prerequisites

- Python 3.10.12 (to match production environment)
- `pipenv` for virtual environment management
- API keys for chosen AI provider (Anthropic Claude, OpenAI, or AWS Bedrock)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/miaomiaozhang20/customer-discovery-interviewer.git
cd customer-discovery-interviewer
```

2. Install dependencies:
```bash
pipenv sync
```

3. Activate the virtual environment:
```bash
pipenv shell
```

4. Set up your secrets (API keys):
```bash
# Copy example secrets file
cp resources/secrets.env.example resources/secrets.env

# Edit resources/secrets.env and add your API keys
# For Anthropic Claude:
ANTHROPIC_API_KEY=your_api_key_here

# For OpenAI:
OPENAI_API_KEY=your_api_key_here

# For AWS Bedrock:
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
```

5. Run the application:
```bash
streamlit run app.py
```

## Configuration

The application is configured via `customer-discovery-interviewer.conf`. Key settings:

- **AI Provider**: Currently set to Anthropic Claude (`claude-3-7-sonnet`)
- **Model Parameters**: Temperature 0.8, max tokens 8192
- **System Prompts**: Located in `resources/` directory
- **Authentication**: Disabled by default (`auth_required: false`)

## File Structure

```
customer-discovery-interviewer/
├── agents.md                              # Agent architecture documentation
├── README.md                              # This file
├── app.py                                 # Main application entry point
├── customer-discovery-interviewer.conf    # Configuration file
├── resources/
│   ├── interviewer_system_prompt.md      # Interviewer agent behavior
│   ├── report_writer_system_prompt.md    # Report writer agent behavior
│   ├── interview_instructions.md         # User instructions
│   └── generate_report_prompt.md         # Report generation prompt
├── libs/                                 # Core libraries
│   ├── streamlit_gui.py                 # Streamlit UI components
│   ├── streamlit_conf.py                # Configuration loader
│   ├── ai_gateways/                     # AI provider integrations
│   │   ├── anthropic_gateway.py
│   │   ├── openai_gateway.py
│   │   └── bedrock_gateway.py
│   └── streamlit_logger.py              # Logging utilities
├── Pipfile                               # Python dependencies
└── Pipfile.lock                          # Locked dependency versions
```

## Usage

### For Founders/Interviewers

1. **Prepare**: Have your product/service description ready (optional upload)
2. **Target Right People**: Interview actual potential customers, not friends/family
3. **Stay Neutral**: Don't pitch, don't lead—just discover
4. **Go Deep**: Don't accept surface-level answers
5. **Listen for Behavior**: Past actions matter more than future promises
6. **Review Report**: Use insights to make informed product decisions

### For Interviewees

1. **Be Honest**: Your feedback helps create better products
2. **Be Specific**: Share real examples and stories
3. **Think Out Loud**: Share your reasoning
4. **Focus on Reality**: Describe what you actually do, not what you might do

## Customer Discovery Principles

This tool embodies key principles from The Mom Test:

1. **Talk about their life, not your idea**
2. **Ask about specifics in the past, not hypotheticals about the future**
3. **Talk less, listen more**
4. **Focus on behavior, not opinions**
5. **Dig for gold: ask "why" multiple times**

## Features

- ✅ Session management (save and resume interviews)
- ✅ PDF upload for product descriptions
- ✅ Progressive warning system for off-topic conversations
- ✅ Downloadable Word document reports
- ✅ Interview and report stage navigation
- ✅ Validation strength assessment (Strong/Moderate/Weak/Invalidation)
- ✅ Direct quote extraction with context
- ✅ Actionable recommendations based on evidence

## Development

### Running in Development Mode

```bash
export DEVELOPMENT_STATE=local-development
streamlit run app.py
```

### Environment Variables

- `DEVELOPMENT_STATE`: Set to `local-development`, `render-development`, or `production`
- `IS_PULL_REQUEST`: Set to `true` for PR testing environments

## Contributing

This project is adapted from [andrewwu55/ai-interviewer](https://github.com/andrewwu55/ai-interviewer) for customer discovery use cases.

To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Submit a pull request

## Reporting Issues

Report bugs or feature requests at: https://github.com/miaomiaozhang20/customer-discovery-interviewer/issues

## Credits

- Original AI Interviewer architecture by andrewwu55
- Customer discovery methodology inspired by:
  - **The Mom Test** by Rob Fitzpatrick
  - **Lean Customer Development** by Cindy Alvarez
  - **Jobs to Be Done** framework
  - Y Combinator startup advice

## License

[Add your license here]

## Architecture Documentation

For detailed information about the agent architecture, roles, functions, and skills, see [agents.md](agents.md).

---

**Built to help founders discover the truth about their ideas—whether that validates or invalidates them.**
