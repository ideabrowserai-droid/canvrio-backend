# CannTech AI Debugging Setup Guide

Your CannTech backend now has AI-powered debugging that automatically analyzes errors using Claude! Here's how to set it up:

## 🚀 Quick Start

### 1. Get Your Anthropic API Key
1. Go to [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign in or create an Anthropic account
3. Navigate to the "API Keys" section
4. Create a new API key or copy your existing one
5. Keep this key secure - you'll need it in the next step

### 2. Set Up Your Environment

**Option A: Using the setup script (Recommended)**
```bash
# Navigate to your project (if not already there)
cd C:\Users\kg\Desktop\canntech-backend

# Run the setup script
setup_ai_debugging.bat
```

**Option B: Manual setup**
```bash
# 1. Navigate to project
cd C:\Users\kg\Desktop\canntech-backend

# 2. Activate virtual environment
venv\Scripts\activate

# 3. Set your API key (replace with your actual key)
set ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here

# 4. Test the setup
python test_ai_debug.py
```

### 3. Start Your Backend with AI Debugging
```bash
python simple_main.py
```

## 🧪 Testing the Setup

Run the test script to verify everything is working:
```bash
python test_ai_debug.py
```

This will check:
- Virtual environment status
- Required packages (anthropic, fastapi, etc.)
- API key configuration
- Connection to Claude API

## 🤖 How AI Debugging Works

Once your backend is running, the AI debugger will:

1. **Automatically catch unexpected errors** in these critical endpoints:
   - `/api/newsletter/subscribe` - Newsletter signup
   - `/api/content/latest` - Content aggregation
   - `/api/content/category/{category}` - Category filtering
   - `/api/content/refresh` - Background refresh
   - `/api/website/analyze` - Cannabis website analysis

2. **Analyze errors with Claude** providing:
   - Root cause analysis
   - Impact assessment for CannTech
   - Specific fix suggestions
   - Prevention strategies
   - Cannabis industry considerations

3. **Log detailed insights** to:
   - Console output (visible when running)
   - `claude_debug.log` file (persistent storage)

## 🔒 Security Features

- **Email addresses are redacted** as `[EMAIL_REDACTED]` in debug logs
- **Sensitive headers** (authorization, api keys) are automatically sanitized
- **API keys and secrets** are filtered out of request data
- **Original error handling preserved** - HTTP exceptions still work normally

## 📁 Files Created

- `setup_ai_debugging.bat` - Quick setup script for Windows
- `test_ai_debug.py` - Test your environment setup
- `.env.example` - Template for environment variables
- `AI_DEBUGGING_SETUP.md` - This guide
- `claude_debug.log` - AI analysis logs (created when first error occurs)

## 🔄 Your Typical Workflow

1. **Open a new terminal**
2. **Navigate to project**: `cd C:\Users\kg\Desktop\canntech-backend`
3. **Activate environment**: `venv\Scripts\activate`
4. **Set API key**: `set ANTHROPIC_API_KEY=your-key-here`
5. **Start backend**: `python simple_main.py`
6. **Interact with your website** - if errors occur, check the console or `claude_debug.log`

## 🆘 Troubleshooting

**"AI debugging unavailable - ANTHROPIC_API_KEY not configured"**
- Make sure you set the environment variable: `set ANTHROPIC_API_KEY=your-key`

**"Failed to initialize Anthropic client"**
- Check your API key is valid and has sufficient credits
- Verify your internet connection

**"Virtual environment not found"**
- Make sure you're in the correct directory: `C:\Users\kg\Desktop\canntech-backend`
- Activate the environment: `venv\Scripts\activate`

## 💡 Tips

- **Keep your terminal open** while developing to see real-time AI analysis
- **Check `claude_debug.log`** for detailed historical analysis of all errors
- **The AI debugging is non-intrusive** - your normal error handling still works
- **Uses Claude Haiku** by default for fast, cost-effective analysis

## 🎯 Example Error Analysis

When an error occurs, you'll see something like:

```
ERROR:simple_main:Newsletter subscription error - AI Analysis: 
**Root Cause Analysis**: Database connection timeout due to high load
**Impact Assessment**: Critical - affects user registration for cannabis newsletter
**Immediate Fix**: Add connection pooling and timeout handling
**Prevention Strategy**: Implement connection retry logic and monitoring
**Cannabis Industry Considerations**: Ensure GDPR compliance maintained during fix
```

Your AI-powered debugging system is now ready! 🚀