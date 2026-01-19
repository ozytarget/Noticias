╔═══════════════════════════════════════════════════════════════╗
║     OZYTARGET NEWS - GitHub Upload Instructions               ║
║            https://github.com/ozytarget/Noticias              ║
╚═══════════════════════════════════════════════════════════════╝

✅ PRE-FLIGHT CHECKLIST
═══════════════════════════════════════════════════════════════════

Before uploading to GitHub, verify:

□ .env file exists and contains your API keys (local only, not in git)
□ .env is in .gitignore (protected)
□ .streamlit/secrets.toml is in .gitignore (protected)
□ news.db is in .gitignore (local database)
□ All documentation files present:
  - README.md
  - CONTRIBUTING.md
  - RAILWAY_DEPLOYMENT.md
  - DEPLOYMENT_STATUS.md
  - .env.example
□ All deployment configs present:
  - Procfile
  - runtime.txt
  - railway.json
  - railway.toml
□ Setup scripts present:
  - deploy-setup.sh (Linux/macOS)
  - deploy-setup.bat (Windows)

═══════════════════════════════════════════════════════════════════

🚀 STEP 1: VERIFY .env IS PROTECTED
═══════════════════════════════════════════════════════════════════

Check that .env file is NOT committed:

PowerShell:
  git status
  
Look for output - .env should NOT appear in file list
If it appears, run:
  git rm --cached .env
  git commit -m "Remove .env from tracking"

═══════════════════════════════════════════════════════════════════

📝 STEP 2: VERIFY GITIGNORE
═══════════════════════════════════════════════════════════════════

Verify .gitignore has these critical lines:

.env
.env.local
.env.*.local
.streamlit/secrets.toml
*.db
*.sqlite
*.sqlite3
__pycache__/
.venv/
venv/
.vscode/
.idea/

Check with:
  git check-ignore .env
  git check-ignore .streamlit/secrets.toml
  git check-ignore news.db

Should print the filename (meaning it's ignored)

═══════════════════════════════════════════════════════════════════

🔐 STEP 3: CREATE .env LOCALLY (if not exists)
═══════════════════════════════════════════════════════════════════

1. Copy template:
   copy .env.example .env

2. Edit .env with your actual API keys:
   GEMINI_API_KEY=sk-...your-actual-key...
   BING_NEWS_API_KEY=...your-actual-key...

3. Verify it's local only:
   git status
   (.env should NOT appear)

═══════════════════════════════════════════════════════════════════

📦 STEP 4: INITIALIZE GIT REPOSITORY (if needed)
═══════════════════════════════════════════════════════════════════

Run this script (one-time setup):

Windows:
  .\deploy-setup.bat

Linux/macOS:
  bash deploy-setup.sh

This will:
  ✅ Initialize Git repository (if not exists)
  ✅ Add GitHub remote
  ✅ Copy .env.example → .env
  ✅ Verify all deployment files

═══════════════════════════════════════════════════════════════════

📤 STEP 5: STAGE & COMMIT FILES
═══════════════════════════════════════════════════════════════════

Add all files to staging:
  git add .

Verify what will be committed (should NOT show .env, secrets, news.db):
  git status

Example output:
  On branch main
  Changes to be committed:
    new file:   README.md
    new file:   CONTRIBUTING.md
    new file:   Procfile
    new file:   requirements.txt
    ... (NO .env, NO secrets.toml, NO *.db)

Commit:
  git commit -m "Initial commit: OZYTARGET NEWS v1.0"

═══════════════════════════════════════════════════════════════════

🌐 STEP 6: PUSH TO GITHUB
═══════════════════════════════════════════════════════════════════

Check remote is configured:
  git remote -v

Should show:
  origin  https://github.com/ozytarget/Noticias.git (fetch)
  origin  https://github.com/ozytarget/Noticias.git (push)

If not configured, add it:
  git remote add origin https://github.com/ozytarget/Noticias.git

Push to GitHub:
  git branch -M main
  git push -u origin main

Wait for push to complete (~10-30 seconds)

═══════════════════════════════════════════════════════════════════

✅ STEP 7: VERIFY GITHUB
═══════════════════════════════════════════════════════════════════

Go to: https://github.com/ozytarget/Noticias

Verify:
□ All files appear in repository
□ README.md shows up as main description
□ .env file does NOT appear (protected by .gitignore)
□ secrets.toml does NOT appear
□ news.db does NOT appear
□ All documentation visible (README, CONTRIBUTING, DEPLOYMENT_STATUS)
□ Code appears (NEWS.py, requirements.txt, Procfile)

═══════════════════════════════════════════════════════════════════

🚀 STEP 8: DEPLOY TO RAILWAY
═══════════════════════════════════════════════════════════════════

Go to: https://railway.app

1. Click "New Project"
2. Select "Deploy from GitHub"
3. Authorize Railway → GitHub
4. Select repository: ozytarget/Noticias
5. Click "Deploy"

Wait for build to complete (~2-3 minutes)

Once deployed:
1. Go to project dashboard
2. Click "Settings" → "Variables"
3. Add environment variables:
   GEMINI_API_KEY = your_key_here
   BING_NEWS_API_KEY = your_key_here (optional)

4. Redeploy to apply variables:
   Click "Deploy" button

5. Get public URL:
   Click "Domains" tab
   Copy generated URL (e.g., your-project.up.railway.app)

═══════════════════════════════════════════════════════════════════

🧪 STEP 9: TEST DEPLOYED APP
═══════════════════════════════════════════════════════════════════

1. Open Railway URL in browser:
   https://your-project.up.railway.app

2. Verify app loads:
   □ See "OZYTARGET NEWS" header
   □ No error messages
   □ UI renders correctly

3. Test functionality:
   □ Click "🔄 Refresh Data" → wait 5-10s
   □ Verify headlines appear
   □ Click "📊 Analyze Headlines" → wait for AI
   □ Verify analysis appears

4. Check logs for errors:
   In Railway dashboard: "Logs" tab
   Should show Streamlit startup messages, no errors

═══════════════════════════════════════════════════════════════════

📋 GIT COMMANDS REFERENCE
═══════════════════════════════════════════════════════════════════

# Show status
git status

# Stage changes
git add .
git add NEWS.py         # Add specific file

# Commit
git commit -m "message"

# Push to GitHub
git push origin main

# Pull latest
git pull origin main

# Check remote
git remote -v

# Add remote
git remote add origin https://github.com/ozytarget/Noticias.git

# View commit history
git log --oneline

# Undo last commit (keep changes)
git reset --soft HEAD~1

# View file history
git log --oneline NEWS.py

═══════════════════════════════════════════════════════════════════

🆘 COMMON ISSUES & FIXES
═══════════════════════════════════════════════════════════════════

Issue: "fatal: not a git repository"
Fix: Run deploy-setup.bat (or .sh)

Issue: ".env appears in git status"
Fix: 
  git rm --cached .env
  git commit -m "Remove .env"

Issue: "Permission denied (publickey)"
Fix: Add SSH key to GitHub account
  Or use HTTPS URL instead of SSH

Issue: "Railway build fails"
Fix: 
  Verify Procfile exists and is correct
  Check requirements.txt format
  See RAILWAY_DEPLOYMENT.md troubleshooting

Issue: "No headlines load on Railway"
Fix:
  Verify environment variables set in Railway dashboard
  Check Railway logs for API errors
  Test GEMINI_API_KEY validity

═══════════════════════════════════════════════════════════════════

📚 NEXT STEPS AFTER DEPLOYMENT
═══════════════════════════════════════════════════════════════════

1. Monitor Railway logs:
   View real-time output, catch errors early

2. Update GitHub README:
   Add deployed URL to README.md

3. Configure custom domain (optional):
   In Railway: Settings → Domains
   Point domain (e.g., news.ozytarget.com)

4. Set up CI/CD (optional):
   GitHub Actions for auto-testing

5. Add GitHub badges to README:
   Build status, version, license, etc.

6. Create GitHub Issues template:
   For bug reports & feature requests

═══════════════════════════════════════════════════════════════════

🎉 YOU'RE DONE!
═══════════════════════════════════════════════════════════════════

✅ Code on GitHub: https://github.com/ozytarget/Noticias
✅ App deployed: https://your-project.up.railway.app
✅ API keys secure (not in repo)
✅ Documentation complete
✅ Ready for production

From now on:
  1. Make code changes locally
  2. Test with: streamlit run NEWS.py
  3. Commit: git add . && git commit -m "message"
  4. Push: git push origin main
  5. Railway auto-deploys!

═══════════════════════════════════════════════════════════════════

Need help?
  - See README.md for general questions
  - See RAILWAY_DEPLOYMENT.md for deployment questions
  - See CONTRIBUTING.md to contribute
  - Check DEPLOYMENT_STATUS.md for checklist

Enjoy your OZYTARGET NEWS app! 🚀

═══════════════════════════════════════════════════════════════════
