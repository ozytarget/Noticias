# OZYTARGET NEWS — Bloomberg-Mode News Aggregator + AI Analysis

A Streamlit-based financial news aggregation and analysis platform powered by Google Gemini AI. Fetches institutional-grade market news from multiple sources, filters by relevance, and generates actionable market insights.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-red)

---

## Features

✅ **Real-Time News Aggregation**
- Multi-source fetching (Google News RSS, Bing News API)
- Auto-refresh every 35 seconds (configurable)
- 24-hour retention with 30-day context storage

✅ **Institutional Filtering**
- 100+ keyword recognition (FOMC, Fed, yields, inflation, options, gamma, liquidity, etc.)
- Noise filtering (meme coins, viral hype, clickbait)
- Source whitelisting (Reuters, Bloomberg, WSJ, FT, etc.)
- Bloomberg-style scoring algorithm

✅ **AI-Powered Analysis (Gemini Pro)**
- Manual headline analysis on-demand
- Custom input analysis (paste any market data)
- Market scenarios (BASE/BULL/BEAR)
- Trading recommendations with confidence levels
- Evidence citation from source headlines

✅ **Database**
- SQLite (development) or PostgreSQL (production)
- Automatic pruning (30-day retention)
- Idempotent digest storage (1/hour max)

---

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)

### Installation

1. **Clone the repo:**
```bash
git clone https://github.com/ozytarget/Noticias.git
cd Noticias
```

2. **Create virtual environment:**
```bash
python -m venv .venv

# Windows
.\.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - GEMINI_API_KEY (required)
# - BING_NEWS_API_KEY (optional)
# - DATABASE_URL (optional for PostgreSQL)
```

5. **Run the app:**
```bash
streamlit run NEWS.py
```

App will be available at: **http://localhost:8501**

---

## Deployment

### Railway (Recommended)

Railway provides a simple, free-tier deployment platform perfect for this app.

#### One-Click Deploy (if available):
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new?repo=https://github.com/ozytarget/Noticias)

#### Manual Deploy:

1. **Push to GitHub:**
```bash
git remote add origin https://github.com/ozytarget/Noticias.git
git branch -M main
git push -u origin main
```

2. **Deploy via Railway:**
   - Go to https://railway.app
   - Click "New Project" → "Deploy from GitHub"
   - Select `ozytarget/Noticias`
   - Railway auto-detects Procfile configuration

3. **Configure Environment Variables** in Railway dashboard:
   - `GEMINI_API_KEY` - Your Google Gemini API key
   - `BING_NEWS_API_KEY` - (Optional) Bing News API key
   - `DATABASE_URL` - (Optional) PostgreSQL connection string for production

4. **Deploy:**
   - Railway auto-deploys on git push
   - App available at: `https://your-project-name.up.railway.app`

**Pricing:**
- Free tier: $5/month or pay-as-you-go
- Plus: includes monthly credit

### Streamlit Cloud (Alternative)

1. Go to https://share.streamlit.io
2. Click "New app" → Select GitHub repo
3. Choose `NEWS.py` as main file
4. Add secrets in dashboard (Settings → Secrets)
5. Done! (Free tier available)

### Heroku (Legacy)

Not recommended due to platform sunset. Use Railway instead.

---

## Configuration

### Auto-Refresh Rate
Edit `NEWS.py` line 20:
```python
AUTO_REFRESH_SECONDS = 35  # Change to desired interval
```

### Keywords
Edit `NEWS.py` line 27:
```python
DEFAULT_KEYWORDS = ["SPY", "FOMC", "Treasury", "yields", ...]
```

### Retention Period
Edit `NEWS.py` line 23:
```python
RETENTION_DAYS = 30  # Keep news for 30 days
```

### Streamlit Config
Edit `.streamlit/config.toml` for UI/server settings

---

## API Keys Required

### 1. Google Gemini API (Required)
- **Get it:** https://makersuite.google.com/app/apikey
- **Free tier:** 60 requests/minute
- **Use case:** AI analysis, headline reasoning, market insights

### 2. Bing News API (Optional)
- **Get it:** https://www.microsoft.com/en-us/bing/apis/bing-news-search-api
- **Free tier:** 1,000 requests/month
- **Use case:** Enhanced news search diversity

### 3. PostgreSQL (Optional - Production)
- Use SQLite (default) for development
- Connect PostgreSQL in production via `DATABASE_URL`

---

## Project Structure

```
APPNEWS/
├── NEWS.py                 # Main Streamlit app
├── requirements.txt        # Python dependencies
├── Procfile               # Railway/Heroku config
├── runtime.txt            # Python version (3.11)
├── railway.json           # Railway-specific config
├── .env.example           # Environment template
├── .env                   # Local secrets (not in git)
├── .gitignore             # Git ignore rules
├── .streamlit/
│   ├── config.toml        # Streamlit UI settings
│   └── secrets.toml       # Streamlit secrets (not in git)
├── README.md              # This file
└── news.db                # SQLite database (local only)
```

---

## How It Works

### Data Pipeline

1. **Fetch** → Google News RSS + Bing News API
2. **Filter** → Institutional keywords + noise removal
3. **Score** → Bloomberg-style ranking algorithm
4. **Store** → SQLite/PostgreSQL with 30-day retention
5. **Analyze** → Gemini AI generates insights on demand

### Scoring Algorithm

Headlines are scored on:
- **Institutional keywords** (+6pts each, max 40pts)
- **High-impact triggers** (+8pts each, max 30pts)
- **Wire phrases** (+8pts each, max 16pts)
- **Whitelist sources** (+18pts)
- **Blacklist sources** (-28pts)
- **Noise keywords** (-10pts each, max -30pts)
- **Clickbait phrases** (-15pts each, max -30pts)
- **Modal weakness** (-6pts each, max -18pts)

**Final range:** -50 to +100

---

## AI Features

### 📊 Headline Analysis (Manual)
- Click "📊 Analyze Headlines" button
- AI reasons over latest 24h + 30d context
- Outputs: CAPTION, REASONING, SCENARIOS, WATCHLIST

### 📰 Custom Data Analysis
- Paste any market data, news, or headlines
- Click "🤖 Analyze Custom Data"
- AI provides: REASONING, BULLISH/BEARISH recs with confidence

### Format: Bloomberg-Style Plain Text
- **CAPTION:** 1-2 line summary
- **REASONING:** 3 claims with evidence citations
- **SCENARIOS:** BASE/BULL/BEAR market outcomes
- **RECOMMENDATIONS:** 4 bullish + 4 bearish assets with price targets

---

## Troubleshooting

### Issue: "AI error: model not found (404)"
**Fix:** Rotate GEMINI_API_KEY or check enabled models in Google AI Studio

### Issue: "No headlines loaded"
**Fix:** Press "🔄 Refresh Data" first, then try AI analysis

### Issue: "Database connection error"
**Fix:** Check DATABASE_URL format if using PostgreSQL; SQLite is default

### Issue: "Empty AI response"
**Fix:** Increase headline count (need ≥8 items). Wait for auto-refresh or press Refresh.

---

## Performance Tips

- **Railway:** Use free tier for testing; upgrade only if needed ($5-20/month)
- **Database:** PostgreSQL faster for 10k+ articles; SQLite fine for <5k
- **AI:** Batch requests every hour (idempotent digest storage)
- **Cache:** Streamlit caches headlines for 35s by default

---

## Development

### Running Tests
```bash
# Lint
pylint NEWS.py

# Syntax check
python -m py_compile NEWS.py
```

### Adding New Features
1. Create feature branch: `git checkout -b feature/my-feature`
2. Edit `NEWS.py`
3. Test locally: `streamlit run NEWS.py`
4. Commit & push: `git push origin feature/my-feature`
5. Open PR on GitHub

---

## Security

- **API Keys:** Never commit `.env` (protected by `.gitignore`)
- **Database:** SQLite auto-reset; PostgreSQL credentials via env vars
- **Dependencies:** Pinned versions in `requirements.txt`
- **Rate Limits:** Google Gemini 60req/min; Bing 1k/month

---

## Support & Links

- **GitHub:** https://github.com/ozytarget/Noticias
- **Deploy:** https://railway.app
- **Gemini API:** https://makersuite.google.com/app/apikey
- **Docs:** See DEPLOYMENT.md

---

## License

Proprietary (ozytarget.com)

---

## Changelog

### v1.0 (2026-01-18)
- ✅ Production-ready
- ✅ Gemini integration with JSON+text output
- ✅ 35s auto-refresh
- ✅ PostgreSQL + SQLite support
- ✅ Bloomberg-style scoring
- ✅ Manual AI triggers
- ✅ Custom data analysis
- ✅ Railway deployment ready

---

**Developed by:** ozy | [ozytarget.com](https://ozytarget.com) | [protdr.com](https://protdr.com)

Last updated: 2026-01-18
