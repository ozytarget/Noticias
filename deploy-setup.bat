@echo off
REM GitHub & Railway Deployment Setup Script (Windows)
REM Usage: deploy-setup.bat

echo.
echo ╔════════════════════════════════════════════════════╗
echo ║  OZYTARGET NEWS - GitHub ^& Railway Setup          ║
echo ╚════════════════════════════════════════════════════╝
echo.

REM Check if git is initialized
if not exist .git (
    echo 🔄 Initializing Git repository...
    git init
    git config user.email "dev@ozytarget.com"
    git config user.name "Ozy Target"
) else (
    echo ✅ Git already initialized
)

REM Check for remote
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo 🔗 Adding GitHub remote...
    set /p REPO_URL="Enter GitHub repo URL (https://github.com/ozytarget/Noticias): "
    if "%REPO_URL%"=="" set REPO_URL=https://github.com/ozytarget/Noticias
    git remote add origin "%REPO_URL%"
    echo ✅ Remote added: %REPO_URL%
) else (
    echo ✅ Git remote already configured
)

REM Check for .env
if not exist .env (
    echo 📝 .env not found. Copy from .env.example...
    copy .env.example .env
    echo ⚠️  IMPORTANT: Edit .env and add your API keys!
) else (
    echo ✅ .env exists
)

REM Verify key files
echo.
echo 📋 Verifying deployment files...
for %%f in (Procfile runtime.txt railway.json railway.toml requirements.txt .gitignore README.md) do (
    if exist "%%f" (
        echo ✅ %%f
    ) else (
        echo ❌ %%f ^(MISSING^)
    )
)

echo.
echo ════════════════════════════════════════════════════
echo 📦 Ready for deployment!
echo ════════════════════════════════════════════════════
echo.
echo Next steps:
echo 1. Edit .env and add your API keys
echo 2. git add .
echo 3. git commit -m "Initial commit - OZYTARGET NEWS"
echo 4. git push -u origin main
echo 5. Deploy to Railway: https://railway.app
echo.
echo For detailed instructions, see:
echo   - README.md ^(local setup^)
echo   - RAILWAY_DEPLOYMENT.md ^(Railway deployment^)
echo.
pause
