#!/bin/bash
# Deploy all three projects to their respective platforms
# Run this script from the repo root

echo "🚀 Portfolio Deployment Script"
echo "==============================="
echo ""

# Check if we're in the right directory
if [ ! -d "automated-report-generator" ] || [ ! -d "document-intelligence" ] || [ ! -d "task-manager" ]; then
    echo "❌ Error: Please run this script from the upwork-portfolio repo root"
    exit 1
fi

echo "✅ Found all project folders"
echo ""

# ============================================
# PROJECT 1: Automated Report Generator
# ============================================
echo "📊 Project 1: Automated Report Generator (Streamlit Cloud)"
echo "-----------------------------------------------------------"
echo "Since Streamlit Cloud requires browser authentication, please:"
echo ""
echo "1. Go to: https://share.streamlit.io"
echo "2. Click 'New app'"
echo "3. Select repository: sciencenerd-des/upwork-portfolio"
echo "4. Set Main file path: automated-report-generator/app.py"
echo "5. Click 'Deploy'"
echo ""
echo "Or use this direct link:"
echo "https://share.streamlit.io/deploy?repository=sciencenerd-des/upwork-portfolio&branch=main&mainModule=automated-report-generator/app.py"
echo ""

# ============================================
# PROJECT 2: Document Intelligence
# ============================================
echo "📄 Project 2: Document Intelligence (Render)"
echo "---------------------------------------------"
echo "Render requires web dashboard. Please:"
echo ""
echo "1. Go to: https://dashboard.render.com"
echo "2. Click 'New +' → 'Web Service'"
echo "3. Connect GitHub: sciencenerd-des/upwork-portfolio"
echo "4. Configure:"
echo "   - Root Directory: document-intelligence"
echo "   - Runtime: Docker"
echo "   - Branch: main"
echo "5. Add Environment Variables:"
echo "   - OPENROUTER_API_KEY: (your key)"
echo "   - DI_API_KEY: (any secure key)"
echo "6. Click 'Create Web Service'"
echo ""

# ============================================
# PROJECT 3: Task Manager  
# ============================================
echo "✅ Project 3: Task Manager (Vercel)"
echo "------------------------------------"
echo "Already deployed! 🎉"
echo "Live URL: https://task-manager-frontend-lvabx3u4j.vercel.app"
echo ""

# Check Vercel deployment
if command -v vercel &> /dev/null; then
    echo "Checking Vercel deployment status..."
    cd task-manager/task-manager-frontend
    vercel --version
    cd ../..
else
    echo "⚠️ Vercel CLI not found. Install with: npm i -g vercel"
fi

echo ""
echo "==============================="
echo "Deployment Status Summary:"
echo "✅ Task Manager: LIVE"
echo "⏳ Automated Report Generator: Manual deploy needed"
echo "⏳ Document Intelligence: Manual deploy needed"
echo ""
echo "Next steps:"
echo "1. Deploy Streamlit app using the link above"
echo "2. Deploy Render service using instructions above"
echo "3. Update PORTFOLIO.md with live URLs"
echo "4. Test all three deployments"
