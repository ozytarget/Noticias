# Contributing to OZYTARGET NEWS

Thank you for your interest in contributing! This document outlines how to get started.

## Code of Conduct

- Be respectful and inclusive
- No spam or commercial promotion
- Focus on quality and maintainability

## Getting Started

### 1. Fork & Clone
```bash
git clone https://github.com/YOUR_USERNAME/Noticias.git
cd Noticias
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Set Up Environment
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # macOS/Linux
pip install -r requirements.txt
```

### 4. Make Changes
- Edit `NEWS.py` or add new modules
- Keep code clean and documented
- Follow PEP 8 style guide

### 5. Test Locally
```bash
streamlit run NEWS.py
```

### 6. Commit & Push
```bash
git add .
git commit -m "Add: brief description of change"
git push origin feature/your-feature-name
```

### 7. Open Pull Request
- Go to GitHub
- Click "Compare & pull request"
- Describe your changes
- Request review from @ozytarget

## What to Contribute

### Bug Fixes
- Issues with headlines fetching
- UI/formatting problems
- AI analysis errors
- Database issues

### Features
- New data sources (news APIs)
- Enhanced filtering algorithms
- Custom themes
- Export functionality
- Mobile optimization

### Documentation
- API key setup guides
- Deployment tutorials
- Troubleshooting tips
- Code comments

### Performance
- Optimize database queries
- Reduce API calls
- Improve caching
- Streamlit session state optimization

## Style Guide

### Python
```python
# Use meaningful variable names
headline_score = calculate_bloomberg_score(item)

# Add docstrings
def filter_institutional(items: list[dict], min_kw: int) -> list[dict]:
    """Filter headlines by institutional keywords."""
    pass

# Type hints
def fetch_news(keywords: list[str]) -> list[dict]:
    pass
```

### Comments
```python
# Good: explains WHY
# Use SHA256 to create unique item identifiers
item_hash = hashlib.sha256(key.encode()).hexdigest()

# Avoid: explains WHAT (code already does that)
# item_hash = hashlib.sha256(key.encode()).hexdigest()
```

## Pull Request Process

1. **Title:** Start with verb (Add/Fix/Update/Remove)
   - ✅ "Add Gemini 2.5 model support"
   - ❌ "fix stuff"

2. **Description:** Explain what & why
   ```markdown
   ## Description
   Adds support for Gemini 2.5 Pro model with improved reasoning
   
   ## Changes
   - Adds gemini-2.5-pro to model selection
   - Updates max tokens to 4500
   - Improves error handling
   
   ## Testing
   - [x] Tested locally with 50+ headlines
   - [x] Verified AI output formatting
   ```

3. **Testing:** Verify locally before submitting
   ```bash
   streamlit run NEWS.py
   # Test: Refresh Data, run AI analysis, try custom input
   ```

4. **No conflicts:** Merge with main before pushing

## Issues & Bug Reports

### Report a Bug
```markdown
**Description:** Brief summary

**Steps to Reproduce:**
1. Click "Refresh Data"
2. Wait 35 seconds
3. See error: ...

**Expected Behavior:**
Headlines should load

**Actual Behavior:**
Error message appears

**Environment:**
- OS: Windows 11
- Python: 3.11
- Streamlit: 1.28.1
```

### Request a Feature
```markdown
**Title:** Clear, concise description

**Use Case:** Why this would be helpful

**Proposed Solution:** How you'd implement it

**Alternatives:** Other approaches considered
```

## Development Tips

### Local Testing
```bash
# Quick test
streamlit run NEWS.py --logger.level=debug

# Test with minimal headlines
# Edit DEFAULT_KEYWORDS in NEWS.py to ["SPY"]
```

### Database
```bash
# Reset local database
rm news.db
streamlit run NEWS.py

# Inspect SQLite
sqlite3 news.db
> SELECT COUNT(*) FROM news_items;
```

### API Testing
```python
# Test Gemini API
python -c "
import os
os.getenv('GEMINI_API_KEY')
# Should print your key
"
```

## Naming Conventions

- **Functions:** `snake_case` 
  - `fetch_google_news()`, `filter_institutional()`
- **Variables:** `snake_case`
  - `latest_news`, `item_score`
- **Constants:** `UPPER_CASE`
  - `AUTO_REFRESH_SECONDS`, `MAX_ARTICLE_AGE_HOURS`
- **Classes:** `PascalCase` (if added)
  - `NewsAggregator`, `AIAnalyzer`

## Commit Message Format

```
Type: Brief description (max 50 chars)

Longer explanation (max 72 chars per line)
- Detail 1
- Detail 2

Fixes #123
```

**Types:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code restructuring
- `docs:` Documentation
- `perf:` Performance improvement
- `chore:` Maintenance

Example:
```
feat: Add support for Gemini 2.5 Pro model

- Updated model selection to prioritize 2.5-pro
- Increased maxOutputTokens to 4500
- Added fallback chain for model availability

Fixes #42
```

## Questions?

- Check [README.md](README.md) for general help
- See [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) for deployment
- Open an issue for questions
- Email: dev@ozytarget.com

## Recognition

Contributors will be listed in:
- CONTRIBUTORS.md
- GitHub Contributors page
- Release notes

---

**Thanks for contributing to OZYTARGET NEWS!** 🚀
