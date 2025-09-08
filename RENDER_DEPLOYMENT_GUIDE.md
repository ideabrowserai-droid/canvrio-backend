# 🚀 CANVRIO BACKEND RENDER DEPLOYMENT GUIDE

## ✅ PREPARATION COMPLETE
Your project is now configured for Render deployment with:
- ✅ `render.yaml` - Deployment configuration 
- ✅ `requirements.txt` - Python dependencies
- ✅ `simple_main.py` - Production-ready backend

---

## 📋 STEP-BY-STEP DEPLOYMENT PROCESS

### PHASE 1: RENDER ACCOUNT SETUP & UPGRADE

#### Step 1: Sign Up/Login to Render
1. Go to **https://render.com**
2. Click "Get Started for Free" or "Sign In"
3. Use GitHub authentication (recommended) or email signup

#### Step 2: Upgrade to Paid Plan
1. Click your profile icon (top right)
2. Select "Account Settings" 
3. Go to "Billing" tab
4. Choose **Starter Plan ($7/month)** - this gives you:
   - Web services that don't sleep
   - Custom domains
   - Persistent disks
   - Priority support

#### Step 3: Add Payment Method
1. Click "Add Payment Method"
2. Enter credit card details
3. Confirm upgrade to Starter plan

---

### PHASE 2: REPOSITORY SETUP

#### Step 4: Push Code to GitHub
1. Open terminal in your project folder: `C:\Users\kg\Desktop\canntech-backend`
2. Initialize git if not already done:
   ```bash
   git add .
   git commit -m "Prepare backend for Render deployment"
   git push origin main
   ```

#### Step 5: Create Render Service
1. In Render dashboard, click **"New +"** 
2. Select **"Web Service"**
3. Click **"Connect GitHub"** and authorize Render
4. Select your repository: `canntech-backend`
5. Click **"Connect"**

---

### PHASE 3: SERVICE CONFIGURATION

#### Step 6: Basic Service Settings
- **Name**: `canvrio-backend`
- **Environment**: `Python 3`
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python src/main/simple_main.py`

#### Step 7: Environment Variables Setup
Click **"Advanced"** → **"Environment Variables"** and add:

| Key | Value | Notes |
|-----|--------|--------|
| `PORT` | `10000` | Required for Render |
| `PYTHON_VERSION` | `3.12.0` | Python version |
| `ANTHROPIC_API_KEY` | `[YOUR_KEY]` | Get from Claude.ai account |

**⚠️ ANTHROPIC_API_KEY Setup:**
1. Go to https://console.anthropic.com
2. Navigate to "API Keys" 
3. Create new key, copy it
4. Paste in Render environment variables

#### Step 8: Health Check Configuration  
- **Health Check Path**: `/health`
- **Auto-Deploy**: ✅ Enable

#### Step 9: Plan Selection
- Select **Starter Plan** (not Free)
- **Region**: Choose closest to your location
- **Disk**: 1GB SSD

---

### PHASE 4: DEPLOYMENT & TESTING

#### Step 10: Deploy Service
1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install Python dependencies 
   - Start your FastAPI server
   - Assign a URL like `https://canvrio-backend.onrender.com`

#### Step 11: Monitor Deployment
- Watch the **"Logs"** tab for deployment progress
- Look for: `INFO: Uvicorn running on http://0.0.0.0:10000`
- First deployment takes ~5-10 minutes

#### Step 12: Test Your Backend
Once deployed, test these endpoints:

✅ **Health Check**: `https://canvrio-backend.onrender.com/health`
- Should return: `{"status": "healthy"}`

✅ **Content API**: `https://canvrio-backend.onrender.com/api/content/latest`  
- Should return: `{"success": true, "content": [...], "count": X}`

✅ **Curator Interface**: `https://canvrio-backend.onrender.com/curator`
- Should show login prompt (user: `canvrio`, pass: `canntech420`)

---

### PHASE 5: CONNECT FRONTEND TO BACKEND

#### Step 13: Update Frontend API Calls
Your Netlify site needs to call your new Render backend:

**In your frontend JavaScript files, change:**
```javascript
// OLD (relative paths - don't work)
fetch('/api/content/latest')

// NEW (full Render URL)
fetch('https://canvrio-backend.onrender.com/api/content/latest')
```

#### Step 14: Enable CORS (Already Done)
Your backend already has CORS enabled for all origins in `simple_main.py`:
```python
app.add_middleware(CORSMiddleware, allow_origins=["*"])
```

---

### PHASE 6: UPDATE UPTIMEROBOT

#### Step 15: Update Monitor
1. Login to UptimeRobot
2. Edit your existing monitor
3. Change URL to: `https://canvrio-backend.onrender.com/health`
4. This will monitor your actual backend, not the static site

---

## 💰 COST BREAKDOWN

**Render Starter Plan: $7/month**
- Web services that stay awake 24/7
- 750 build hours/month  
- 750GB bandwidth/month
- Custom domains
- SSL certificates

**Total Monthly Cost: $7**
- No additional charges for API calls
- Automatic scaling included
- Much cheaper than AWS/GCP for small apps

---

## 🛠️ POST-DEPLOYMENT CHECKLIST

After successful deployment:

- [ ] Health endpoint responds: `/health`
- [ ] Content API works: `/api/content/latest`  
- [ ] Curator login works: `/curator`
- [ ] UptimeRobot monitoring new backend
- [ ] Frontend updated to call Render backend
- [ ] News banners loading on your website

---

## 🚨 TROUBLESHOOTING

**Build Fails?**
- Check "Logs" tab for Python dependency errors
- Ensure `requirements.txt` has correct versions

**Service Won't Start?**  
- Check if `PORT=10000` environment variable is set
- Verify `simple_main.py` path in start command

**Database Errors?**
- SQLite files will be created automatically
- Check disk space (1GB allocated)

**API Calls Fail?**
- Ensure frontend uses full Render URL  
- Check CORS settings in browser console

---

## 🎯 SUCCESS INDICATORS

You'll know it worked when:

1. **UptimeRobot shows "UP"** for your backend health check
2. **News banners populate** with live content on canvrio.ca
3. **Curator interface** loads and functions properly
4. **Content refresh** works automatically

---

**Total Setup Time: ~30 minutes**  
**Monthly Cost: $7**  
**Uptime: 99.9%+ guaranteed**

Ready to deploy? Follow the steps above in order! 🚀