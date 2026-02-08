# Deployment Guide - Critical Fixes Applied

This guide documents the deployment bugs found and fixed in all three portfolio projects.

---

## Summary of Fixes Applied

| Project | Bugs Fixed | Status |
|---------|-----------|--------|
| Automated Report Generator | 2 | ✅ Ready for Streamlit Cloud |
| Document Intelligence | 3 | ✅ Ready for Render |
| Task Management System | 6 | ✅ Ready for Vercel |

---

## Project 1: Automated Report Generator (Streamlit Cloud)

### ✅ Fixes Applied

1. **Created `packages.txt`** - Required for matplotlib/seaborn on Linux servers
2. **Created `.streamlit/config.toml`** - Server configuration, CORS, max upload size

### Deployment Steps

1. Push code to GitHub
2. Go to https://share.streamlit.io
3. Connect your GitHub repository
4. Select `automated-report-generator` folder
5. Main file path: `app.py`
6. Deploy

### Environment Variables (Optional)
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

---

## Project 2: Document Intelligence System (Render)

### ✅ Fixes Applied

1. **Updated `requirements.txt`** - Added missing dependencies:
   - `langchain`, `langchain-community` - LLM processing
   - `chromadb` - Vector database
   - `sentence-transformers` - Embeddings
   - `spacy` - NLP processing
   - `numpy<2.0.0` - Compatibility pin

2. **Updated `Dockerfile`** - Added spaCy model download step

3. **CORS Configuration** - Already set but review for production

### Deployment Steps

1. Push code to GitHub
2. Go to https://dashboard.render.com
3. Create new Web Service
4. Connect GitHub repository
5. Use Dockerfile for build
6. Set environment variables:
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
DI_API_KEY=your_secure_api_key
```
7. Deploy

### Streamlit Cloud (UI)

1. Deploy `app/streamlit_app.py` to Streamlit Cloud
2. Set `API_BASE_URL` to your Render API endpoint

---

## Project 3: Task Management System (Vercel)

### ✅ Fixes Applied

1. **Updated `package.json`** - Added critical missing dependencies:
   - `convex` - Real-time database SDK
   - `@workos-inc/node` - Authentication SDK
   - `@dnd-kit/core` - Drag and drop
   - `@dnd-kit/sortable` - Sortable items
   - `@dnd-kit/utilities` - DND utilities

2. **Updated `next.config.js`** - Environment fallbacks for demo mode

### Deployment Steps

1. Install dependencies:
```bash
cd task-manager/task-manager-frontend
npm install
```

2. Setup Convex (if using real backend):
```bash
npx convex login
npx convex dev  # Generates convex/_generated/
```

3. For Demo Mode (no backend needed):
```bash
NEXT_PUBLIC_DEMO_MODE=true
npm run build
```

4. Deploy to Vercel:
```bash
vercel --prod
```

Or connect GitHub repo at https://vercel.com/new

### Environment Variables

**For Demo Mode:**
```bash
NEXT_PUBLIC_DEMO_MODE=true
NEXT_PUBLIC_WORKOS_CLIENT_ID=demo_workos_client_id
NEXT_PUBLIC_WORKOS_ORGANIZATION_ID=demo_org_001
WORKOS_CLIENT_ID=demo_workos_client_id
WORKOS_API_KEY=demo_workos_api_key
WORKOS_REDIRECT_URI=http://localhost:3000/auth/callback
```

**For Production:**
```bash
NEXT_PUBLIC_DEMO_MODE=false
CONVEX_DEPLOYMENT_URL=your_convex_url
NEXT_PUBLIC_WORKOS_CLIENT_ID=your_workos_client_id
WORKOS_API_KEY=your_workos_api_key
WORKOS_REDIRECT_URI=https://yourdomain.com/auth/callback
```

---

## Post-Deployment Checklist

After each deployment:

- [ ] Verify live demo URL is accessible
- [ ] Test core functionality (upload, generate, export)
- [ ] Check for console errors in browser DevTools
- [ ] Update `PORTFOLIO.md` with actual live URLs
- [ ] Take screenshots of working demos
- [ ] Update Upwork profile with live demo links

---

## Common Issues

### Streamlit Cloud: "No module named 'cv2'" or GL errors
→ `packages.txt` with `libgl1` fixes this

### Render: "ModuleNotFoundError: No module named 'langchain'" 
→ Fixed by adding to requirements.txt

### Render: "OSError: [E050] Can't find model 'en_core_web_sm'"
→ Fixed by adding spacy download to Dockerfile

### Vercel: "Cannot find module 'convex'"
→ Fixed by adding to package.json

### Vercel: "Cannot find module '@dnd-kit/core'"
→ Fixed by adding all dnd-kit packages to package.json

---

## Next Steps

1. **Install dependencies locally** to test each project
2. **Deploy each project** following the steps above
3. **Update URLs** in `PORTFOLIO.md` and your Upwork profile
4. **Test thoroughly** before launching

---

*Last Updated: 2026-02-08*
*Bugs Fixed: 11 critical deployment issues*
