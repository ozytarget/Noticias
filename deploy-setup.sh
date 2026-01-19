#!/bin/bash
# GitHub & Railway Deployment Setup Script
# Usage: bash deploy-setup.sh

echo "╔════════════════════════════════════════════════════╗"
echo "║  OZYTARGET NEWS - GitHub & Railway Setup          ║"
echo "╚════════════════════════════════════════════════════╝"

# Check if git is initialized
if [ ! -d .git ]; then
    echo "🔄 Initializing Git repository..."
    git init
    git config user.email "dev@ozytarget.com"
    git config user.name "Ozy Target"
else
    echo "✅ Git already initialized"
fi

# Check for remote
if ! git remote | grep -q origin; then
    echo "🔗 Adding GitHub remote..."
    read -p "Enter GitHub repo URL (https://github.com/ozytarget/Noticias): " REPO_URL
    REPO_URL=${REPO_URL:-https://github.com/ozytarget/Noticias}
    git remote add origin "$REPO_URL"
    echo "✅ Remote added: $REPO_URL"
else
    echo "✅ Git remote already configured"
fi

# Check for .env
if [ ! -f .env ]; then
    echo "📝 .env not found. Copy from .env.example..."
    cp .env.example .env
    echo "⚠️  IMPORTANT: Edit .env and add your API keys!"
else
    echo "✅ .env exists"
fi

# Verify key files
echo ""
echo "📋 Verifying deployment files..."
files=("Procfile" "runtime.txt" "railway.json" "railway.toml" "requirements.txt" ".gitignore" "README.md")
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (MISSING)"
    fi
done

echo ""
echo "════════════════════════════════════════════════════"
echo "📦 Ready for deployment!"
echo "════════════════════════════════════════════════════"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. git add ."
echo "3. git commit -m 'Initial commit - OZYTARGET NEWS'"
echo "4. git push -u origin main"
echo "5. Deploy to Railway: https://railway.app"
echo ""
echo "For detailed instructions, see:"
echo "  - README.md (local setup)"
echo "  - RAILWAY_DEPLOYMENT.md (Railway deployment)"
echo ""
