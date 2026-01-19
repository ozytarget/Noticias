# Railway Deployment Guide — OZYTARGET NEWS

## Pre-Deployment Checklist

- [x] Push to GitHub: https://github.com/ozytarget/Noticias
- [ ] Create Railway account: https://railway.app (free tier)
- [ ] Have API keys ready:
  - GEMINI_API_KEY (required)
  - BING_NEWS_API_KEY (optional)

---

## Step 1: Create Railway Project

1. Go to https://railway.app
2. Click **"New Project"**
3. Select **"Deploy from GitHub"**
4. Authorize Railway to access your GitHub account
5. Select **`ozytarget/Noticias`** repo

---

## Step 2: Configure Environment Variables

Railway will auto-detect the `Procfile`. Now add your secrets:

1. In Railway dashboard, click **Settings** → **Variables**
2. Add each key-value pair:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
BING_NEWS_API_KEY=your_actual_bing_api_key
DATABASE_URL=postgresql://...  # (optional, for advanced setup)
```

**Where to get API keys:**

### GEMINI_API_KEY (REQUIRED)
- Go: https://makersuite.google.com/app/apikey
- Click "Create API Key"
- Copy and paste here

### BING_NEWS_API_KEY (OPTIONAL)
- Go: https://www.microsoft.com/en-us/bing/apis/bing-news-search-api
- Create free account
- Copy subscription key

### DATABASE_URL (OPTIONAL)
- Default: Uses SQLite (fine for low volume)
- For PostgreSQL: Copy connection string from your DB provider
- Format: `postgresql://username:password@host:port/dbname`

---

## Step 3: Deploy

1. Click **"Deploy"** in Railway dashboard
2. Wait for build (~2-3 minutes)
3. Once deployed, you'll get a public URL:
   ```
   https://your-project-name.up.railway.app
   ```

---

## Step 4: Verify Deployment

1. Open your Railway URL in browser
2. Look for "OZYTARGET NEWS" header
3. Click **"🔄 Refresh Data"** to verify API connectivity
4. Check browser console (F12) for any errors

---

## Continuous Deployment

Railway auto-deploys on every git push:

```bash
# Make changes locally
git add .
git commit -m "Update keywords"
git push origin main

# Railway automatically rebuilds & redeploys
```

---

## Troubleshooting

### Issue: Build fails with "No module named streamlit"
**Fix:** Check `requirements.txt` is in root directory

### Issue: "GEMINI_API_KEY not found" error
**Fix:** Verify variable name exactly matches (case-sensitive)

### Issue: App loads but no headlines
**Fix:** Check Railway Variables; refresh page; wait 40s for auto-fetch

### Issue: "503 Service Unavailable"
**Fix:** Railway might be redeploying. Wait 2-3 minutes.

### Issue: Database connection errors
**Fix:** Don't set DATABASE_URL (uses SQLite by default)

---

## Monitoring & Logs

1. Click **"Logs"** in Railway dashboard
2. See real-time output from Streamlit
3. Check for errors or slow queries

---

## Free Tier Limitations

- **$5/month credit** (or pay-as-you-go)
- **Up to 4GB RAM** per deployment
- **50GB bandwidth/month** (usually sufficient)
- Always-on apps count towards credits

**Estimate for this app:**
- Typical: $1-3/month on free tier
- Upgrade only if needed for multiple apps

---

## Pro Tips

### 1. Use GitHub secrets for local development
```bash
# Never commit .env to GitHub!
# Railway uses environment variables instead
```

### 2. Auto-refresh for latest code
```bash
# Push to GitHub
git push origin main

# Railway redeploys automatically (~1-2 min)
```

### 3. Scale the app
- If traffic increases, Railway auto-scales
- No manual configuration needed

### 4. Database backup
- SQLite data is ephemeral (lost on redeploy)
- Use PostgreSQL for persistent storage:
  - Add `DATABASE_URL` variable
  - Connect to managed DB (Railway, Vercel Postgres, etc.)

---

## Custom Domain (Optional)

1. In Railway: **Settings** → **Domains**
2. Add custom domain (e.g., `news.ozytarget.com`)
3. Update DNS records at your registrar
4. SSL auto-enabled

---

## Advanced: PostgreSQL Database

For production with data persistence:

### Option A: Railway Postgres
1. In Railway: **+ New** → **Postgres**
2. Copy `DATABASE_URL`
3. Add to Variables in your app project
4. Redeploy

### Option B: External Provider
- Supabase, Render, PlanetScale, etc.
- Copy connection string
- Paste in Railway Variables

---

## Rollback to Previous Version

1. In Railway: **Deployments**
2. Find previous working version
3. Click **"Redeploy"**
4. App reverts instantly

---

## Support

- **Railway Docs:** https://docs.railway.app
- **Streamlit Deploy:** https://docs.streamlit.io/deploy
- **GitHub Issues:** https://github.com/ozytarget/Noticias/issues

---

**Last updated:** 2026-01-18
