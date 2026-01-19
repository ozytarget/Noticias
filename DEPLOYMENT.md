# Deployment Guide - NEWS App

## Overview
This is a Streamlit-based news aggregation application with AI-powered digests using Google Gemini API.

## Deployment Platforms

### 1. Railway (Recommended)
```bash
# Prerequisites
- Railway account (https://railway.app)
- Git repository

# Steps
1. Push to GitHub
2. Go to https://railway.app
3. Create new project
4. Connect GitHub repository
5. Set environment variables:
   - BING_NEWS_API_KEY: Your Bing News API key
   - GEMINI_API_KEY: Your Google Gemini API key
   - DATABASE_URL: PostgreSQL connection string (optional, uses SQLite by default)
6. Deploy

# Pricing: Free tier + Pay-as-you-go ($5/month minimum)
```

### 2. Streamlit Cloud
```bash
# Prerequisites
- Streamlit account
- GitHub repository

# Steps
1. Push to GitHub
2. Go to https://share.streamlit.io
3. Click "New app"
4. Connect your GitHub repo
5. Select "NEWS.py" as the main file
6. Set secrets in dashboard:
   - BING_NEWS_API_KEY
   - GEMINI_API_KEY
7. Deploy (automatic)

# Pricing: Free tier available
```

### 3. Heroku (Legacy - shutting down)
Not recommended due to platform changes.

## Environment Variables Required

```env
BING_NEWS_API_KEY=your_bing_api_key
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=postgresql://...  # Optional, uses SQLite if not set
```

## Database
- **Development**: SQLite (news.db)
- **Production**: PostgreSQL recommended for better performance

## Local Testing Before Deployment

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the app
streamlit run NEWS.py

# App will be available at http://localhost:8501
```

## Files Structure
- `NEWS.py` - Main application
- `requirements.txt` - Python dependencies
- `.env` - Local environment variables (NOT committed)
- `.streamlit/config.toml` - Streamlit configuration
- `Procfile` - Heroku/Railway process definition
- `runtime.txt` - Python version specification
- `railway.json` - Railway configuration

## Troubleshooting

### Common Issues
1. **Import errors**: Ensure all packages in requirements.txt are installed
2. **API key errors**: Check environment variables are set correctly
3. **Database connection**: Verify DATABASE_URL format if using PostgreSQL

## Support
See CHECKLIST.txt for project completion status.
