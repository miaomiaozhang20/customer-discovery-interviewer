# Deployment Guide

## Deploy to Streamlit Community Cloud (Recommended - Free)

Streamlit Community Cloud is the easiest way to deploy your customer discovery interviewer and make it publicly accessible.

### Prerequisites
- GitHub account (you already have: miaomiaozhang20)
- Anthropic API key (or OpenAI/AWS Bedrock key)

### Step-by-Step Deployment

#### 1. Get Your API Key

**For Anthropic Claude (Recommended):**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key (you'll need it in step 4)

**For OpenAI (Alternative):**
1. Go to https://platform.openai.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new secret key
5. Copy the key

#### 2. Sign Up for Streamlit Community Cloud

1. Go to https://streamlit.io/cloud
2. Click "Sign up" or "Get started"
3. Sign in with your GitHub account (miaomiaozhang20)
4. Authorize Streamlit to access your GitHub repositories

#### 3. Deploy Your App

1. Click "New app" button
2. Select your repository: `miaomiaozhang20/customer-discovery-interviewer`
3. Set the main file path: `app.py`
4. Set the branch: `main`
5. Click "Advanced settings" (optional)
   - Set Python version: `3.10`
6. Click "Deploy!"

#### 4. Add Your Secrets (API Keys)

**IMPORTANT**: Do this immediately after deployment starts

1. In the Streamlit Cloud dashboard, click on your app
2. Click the "⋮" menu (three dots) in the top right
3. Select "Settings"
4. Click on "Secrets" in the left sidebar
5. Add your secrets in TOML format:

```toml
ANTHROPIC_API_KEY = "your-actual-api-key-here"
```

Or if using OpenAI:
```toml
OPENAI_API_KEY = "your-actual-api-key-here"
```

Or if using AWS Bedrock:
```toml
AWS_ACCESS_KEY_ID = "your-access-key"
AWS_SECRET_ACCESS_KEY = "your-secret-key"
AWS_DEFAULT_REGION = "us-east-1"
```

6. Click "Save"

#### 5. Your App is Live!

Your app will be available at:
```
https://customer-discovery-interviewer.streamlit.app
```

Or a similar URL assigned by Streamlit Cloud.

### Updating Your Live App

Any changes you push to the `main` branch on GitHub will automatically trigger a redeployment:

```bash
# Make your changes
git add .
git commit -m "Your change description"
git push

# App will redeploy automatically in ~1-2 minutes
```

### Managing Your Deployment

**View Logs:**
1. Go to your app in Streamlit Cloud dashboard
2. Click "Manage app"
3. View real-time logs

**Restart App:**
1. Go to "Manage app"
2. Click "Reboot app"

**Take App Offline:**
1. Go to "Settings"
2. Click "Delete app"

### Resource Limits (Free Tier)

Streamlit Community Cloud free tier includes:
- ✅ Unlimited public apps
- ✅ 1 GB RAM per app
- ✅ 1 CPU per app
- ✅ Unlimited viewers
- ✅ Automatic HTTPS
- ✅ Custom domain support

### Troubleshooting

**App won't start:**
- Check logs for errors
- Verify API keys are set correctly in Secrets
- Ensure requirements.txt has all dependencies

**App is slow:**
- Free tier has limited resources
- Consider upgrading to Streamlit Cloud paid tier if needed

**API errors:**
- Verify API key is valid and has credits
- Check API rate limits

**Import errors:**
- Ensure all dependencies are in requirements.txt
- Check Python version is 3.10

---

## Alternative Deployment Options

### Option 2: Render

1. Go to https://render.com/
2. Sign up with GitHub
3. Create new "Web Service"
4. Connect your repository
5. Set build command: `pip install -r requirements.txt`
6. Set start command: `streamlit run app.py --server.port $PORT`
7. Add environment variables for API keys
8. Deploy

### Option 3: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: streamlit run app.py --server.port $PORT
   ```
3. Create `setup.sh`:
   ```bash
   mkdir -p ~/.streamlit/
   echo "[server]
   headless = true
   port = $PORT
   enableCORS = false
   " > ~/.streamlit/config.toml
   ```
4. Deploy:
   ```bash
   heroku create customer-discovery-interviewer
   heroku config:set ANTHROPIC_API_KEY=your_key
   git push heroku main
   ```

### Option 4: Self-Hosted (AWS/GCP/Azure)

1. Set up a virtual machine
2. Install Python 3.10 and dependencies
3. Run with: `streamlit run app.py --server.port 8501`
4. Configure reverse proxy (nginx) and SSL
5. Set up domain and firewall rules

---

## Sharing Your App

Once deployed, you can:
- Share the URL directly with users
- Embed in your website with an iframe
- Add to your GitHub README as a badge
- Share on social media

### Add App Badge to README

Add this to your README.md:

```markdown
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://customer-discovery-interviewer.streamlit.app)
```

---

## Security Best Practices

✅ **DO:**
- Store API keys in Streamlit Secrets (never in code)
- Keep your repository public for Community Cloud
- Use environment variables for sensitive data
- Monitor API usage and costs
- Set API rate limits if possible

❌ **DON'T:**
- Commit API keys to Git
- Share your secrets.toml file
- Expose internal configurations
- Use personal API keys for public apps

---

## Cost Management

**Streamlit Community Cloud:** Free
**Anthropic API:** Pay per token
**OpenAI API:** Pay per token

Monitor your API usage:
- Anthropic: https://console.anthropic.com/settings/billing
- OpenAI: https://platform.openai.com/usage

Set spending limits to avoid unexpected charges.

---

## Getting Help

- Streamlit Community: https://discuss.streamlit.io/
- Streamlit Docs: https://docs.streamlit.io/
- Report Issues: https://github.com/miaomiaozhang20/customer-discovery-interviewer/issues

---

**Your customer discovery interviewer will be live and accessible to anyone worldwide! 🌍**
