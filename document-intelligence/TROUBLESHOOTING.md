# Troubleshooting Guide

## Common Issues and Solutions

### 1. urllib3 v2 SSL Warning (macOS)

**Error:**
```
NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently 'ssl' module is compiled with 'LibreSSL 2.8.3'.
```

**Cause:**
macOS uses LibreSSL instead of OpenSSL, which is incompatible with urllib3 v2.

**Solution:**
The `requirements.txt` file now includes `urllib3<2.0.0` which is compatible with LibreSSL. Simply reinstall:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Verify:**
```bash
python -c "import urllib3; print(urllib3.__version__)"
# Should print: 1.26.20 (or similar 1.x version)
```

---

### 2. Tesseract Not Found

**Error:**
```
Tesseract binary not found. OCR will not work.
```

**Cause:**
Tesseract OCR is not installed on your system.

**Solution:**

**macOS:**
```bash
brew install tesseract tesseract-lang
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-eng
```

**Windows:**
1. Download Tesseract from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Install Tesseract
3. Add Tesseract installation directory to system PATH
4. Example: `C:\Program Files\Tesseract-OCR`

**Verify:**
```bash
tesseract --version
# Should print version information
```

**Python:**
```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version())"
# Should print version number
```

---

### 3. spaCy Model Missing

**Error:**
```
No spaCy model available. Using basic sentence splitting.
```

**Cause:**
spaCy language model is not downloaded.

**Solution:**
```bash
source venv/bin/activate
python -m spacy download en_core_web_sm
```

**Verify:**
```bash
python -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('Model loaded successfully')"
# Should print: Model loaded successfully
```

**Alternative Models:**
For better accuracy (larger models):
```bash
python -m spacy download en_core_web_md    # Medium model
python -m spacy download en_core_web_lg    # Large model
```

---

### 4. Import Errors After Installation

**Error:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Cause:**
Dependencies not installed or virtual environment not activated.

**Solution:**
```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

### 5. Port Already in Use

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Cause:**
Another application is using the port (default: 8501 for Streamlit, 8000 for FastAPI).

**Solution:**

**Find process:**
```bash
lsof -i :8501  # For Streamlit
lsof -i :8000  # For FastAPI
```

**Kill process:**
```bash
kill -9 <PID>
```

**Or use a different port:**
```bash
streamlit run app/streamlit_app.py --server.port 8502
uvicorn app.main:app --port 8001
```

---

### 6. PDF Loading Issues

**Error:**
```
Error loading PDF: Unsupported file format
```

**Cause:**
Corrupted PDF or unsupported PDF version.

**Solution:**
1. Verify the PDF is not password-protected
2. Try opening the PDF in a browser to confirm it's valid
3. Check file size (extremely large files may timeout)
4. Try converting PDF to images and processing individually

---

### 7. OCR Poor Results

**Symptom:**
OCR extracts text incorrectly or with many errors.

**Solutions:**

1. **Improve image quality:**
   - Ensure images are high resolution (300 DPI minimum)
   - Good lighting and contrast
   - No blurred or distorted text

2. **Preprocessing:**
   - The OCR engine includes automatic preprocessing
   - For better results, convert images to black and white
   - Deskew documents if text is rotated

3. **Language model:**
   ```bash
   # Install additional language packs
   brew install tesseract-lang  # macOS
   sudo apt-get install tesseract-ocr-all  # Linux
   ```

4. **Custom Tesseract config:**
   ```python
   import pytesseract
   custom_config = r'--oem 3 --psm 6'
   text = pytesseract.image_to_string(image, config=custom_config)
   ```

---

### 8. Memory Errors with Large Documents

**Error:**
```
MemoryError or Process finished with exit code 137
```

**Cause:**
Processing very large documents exhausts available memory.

**Solutions:**

1. **Chunk processing:**
   - The system automatically chunks large documents
   - Adjust chunk size in `config/settings.yaml`

2. **Process pages separately:**
   ```python
   # Process PDF page by page
   for page in pdf_document:
       process_page(page)
   ```

3. **Increase system memory:**
   - Close other applications
   - Increase Docker/container memory limits
   - Use a machine with more RAM

---

### 9. API Key Errors

**Error:**
```
OpenRouter API key not found. Using fallback summarization.
```

**Cause:**
Environment variable not set or .env file not configured.

**Solution:**

1. **Create .env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   OPENROUTER_API_KEY=your_actual_api_key_here
   ```

3. **Restart application:**
   ```bash
   # Stop current instance and restart
   streamlit run app/streamlit_app.py
   ```

4. **Verify:**
   ```bash
   python -c "import os; print(os.environ.get('OPENROUTER_API_KEY', 'Not found'))"
   ```

---

### 10. Vector Store Errors (ChromaDB)

**Error:**
```
ChromaDB connection error or embedding generation failed
```

**Cause:**
Missing `sentence-transformers` model or disk space issue.

**Solution:**

1. **Verify sentence-transformers installed:**
   ```bash
   source venv/bin/activate
   pip install sentence-transformers
   ```

2. **Check disk space:**
   ```bash
   df -h  # Check available disk space
   ```

3. **Clear cache:**
   ```bash
   rm -rf ~/.cache/huggingface
   rm -rf ~/.cache/chroma
   ```

---

## Getting Help

If you encounter issues not covered here:

1. Check the [README.md](README.md) for complete setup instructions
2. Review the [PRD document](DI-PRD.md) for system requirements
3. Check GitHub issues or create a new one
4. Include the following information in bug reports:
   - OS and version
   - Python version
   - Full error traceback
   - Steps to reproduce

---

## Development Environment Issues

### Virtual Environment Not Working

**Symptom:**
Commands fail even after activating venv.

**Solutions:**

1. **Recreate virtual environment:**
   ```bash
   rm -rf venv
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Check Python version in venv:**
   ```bash
   source venv/bin/activate
   python --version
   # Should show Python 3.9+
   ```

3. **Update pip:**
   ```bash
   pip install --upgrade pip
   ```

### Tests Failing

**Symptom:**
Tests fail with import errors or assertion failures.

**Solutions:**

1. **Install test dependencies:**
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **Run tests with verbose output:**
   ```bash
   pytest tests/ -v -s
   ```

3. **Check test environment:**
   ```bash
   pytest tests/ --collect-only
   # Lists all available tests
   ```

---

## Performance Issues

### Slow Document Processing

**Causes and Solutions:**

1. **Large files:**
   - Use smaller test files first
   - Increase timeout settings

2. **OCR bottleneck:**
   - OCR is CPU-intensive
   - Consider disabling OCR for born-digital PDFs

3. **Embedding generation:**
   - Large documents require many embeddings
   - Use smaller chunk sizes

4. **System resources:**
   - Check CPU/RAM usage
   - Close other applications
   - Use a machine with better specs

### API Rate Limiting

**Symptom:**
OpenRouter API returns 429 errors.

**Solution:**
- The system includes automatic retry logic
- Add your own API key to avoid rate limits
- Consider using a faster plan

---

## Security Notes

### API Key Exposure

**Warning:**
Never commit `.env` file to version control.

**Solution:**
- `.env` is listed in `.gitignore`
- Use environment variables in production
- Rotate compromised keys immediately

### File Upload Security

**Note:**
The system processes files in memory only.
- No persistent storage
- Files deleted after session
- Scan uploaded files for malware in production

---

## Contact & Support

For additional help:
- Check project documentation
- Review example code in `tests/` directory
- Create GitHub issue with details
