"""
FastAPI Integration Tests for Document Intelligence API.
Tests all API endpoints using TestClient with generated in-memory PDFs.
"""

import sys
import io
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def create_test_pdf(text: str = "Test document content") -> bytes:
    """Create a simple PDF for testing."""
    import fitz
    
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text, fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


def create_test_image() -> bytes:
    """Create a simple test image."""
    from PIL import Image
    
    img = Image.new("RGB", (100, 100), color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check_returns_ok(self):
        """Test that health check returns success."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
        assert "checks" in data
        assert "timestamp" in data

    def test_health_check_includes_dependency_status(self):
        """Test that health check includes dependency checks."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        data = response.json()
        checks = data.get("checks", {})
        
        assert "tesseract" in checks
        assert "spacy" in checks
        assert "chromadb" in checks


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self):
        """Test that root returns API information."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data


class TestUploadEndpoint:
    """Tests for document upload endpoint."""

    def test_upload_pdf_success(self):
        """Test successful PDF upload."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        pdf_content = create_test_pdf("Hello World Test")
        
        response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "doc_id" in data
        assert "message" in data
        assert data["status"] in ["pending", "processing"]

    def test_upload_image_success(self):
        """Test successful image upload."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        image_content = create_test_image()
        
        response = client.post(
            "/upload",
            files={"file": ("test.png", image_content, "image/png")}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "doc_id" in data

    def test_upload_unsupported_format(self):
        """Test upload of unsupported file format."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.post(
            "/upload",
            files={"file": ("test.txt", b"text content", "text/plain")}
        )
        
        assert response.status_code == 400
        assert "Unsupported" in response.json()["detail"]

    def test_upload_oversized_file(self):
        """Test upload of oversized file."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Create a large content (simulating >25MB)
        # Note: This may be slow, so we use a smaller mock
        with patch('src.document_loader.DocumentLoader.validate_file') as mock_validate:
            mock_result = MagicMock()
            mock_result.is_valid = False
            mock_result.error_message = "File size exceeds maximum"
            mock_validate.return_value = mock_result
            
            response = client.post(
                "/upload",
                files={"file": ("large.pdf", b"content", "application/pdf")}
            )
            
            assert response.status_code == 400


class TestStatusEndpoint:
    """Tests for document status endpoint."""

    def test_get_status_valid_doc(self):
        """Test getting status of valid document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # First upload a document
        pdf_content = create_test_pdf()
        upload_response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        
        doc_id = upload_response.json()["doc_id"]
        
        # Get status
        response = client.get(f"/status/{doc_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "doc_id" in data
        assert "status" in data

    def test_get_status_invalid_doc(self):
        """Test getting status of non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/status/nonexistent123")
        
        assert response.status_code == 404


class TestSummaryEndpoint:
    """Tests for document summary endpoint."""

    def test_get_summary_not_found(self):
        """Test getting summary of non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/summary/nonexistent123")
        
        assert response.status_code == 404


class TestEntitiesEndpoint:
    """Tests for entities extraction endpoint."""

    def test_get_entities_not_found(self):
        """Test getting entities of non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/entities/nonexistent123")
        
        assert response.status_code == 404


class TestQAEndpoint:
    """Tests for Q&A endpoint."""

    def test_qa_document_not_found(self):
        """Test Q&A with non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.post(
            "/qa/nonexistent123",
            json={"question": "What is this about?"}
        )
        
        assert response.status_code == 404

    def test_qa_empty_question(self):
        """Test Q&A with empty question."""
        from fastapi.testclient import TestClient
        from app.main import app
        from src.document_store import get_document_store, reset_document_store
        
        reset_document_store()
        client = TestClient(app)
        
        # Upload a document first
        pdf_content = create_test_pdf("Test content")
        upload_response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        
        doc_id = upload_response.json()["doc_id"]
        
        # Wait for processing
        time.sleep(1)
        
        response = client.post(
            f"/qa/{doc_id}",
            json={"question": ""}
        )
        
        # Should return 400 for empty question
        assert response.status_code in [400, 422]


class TestExportEndpoint:
    """Tests for export endpoint."""

    def test_export_not_found(self):
        """Test export of non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/export/nonexistent123/json")
        
        assert response.status_code == 404

    def test_export_invalid_format(self):
        """Test export with invalid format."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.get("/export/someid/invalid_format")
        
        # Should return 422 for invalid enum value
        assert response.status_code == 422


class TestDeleteEndpoint:
    """Tests for document deletion endpoint."""

    def test_delete_document(self):
        """Test deleting a document."""
        from fastapi.testclient import TestClient
        from app.main import app
        from src.document_store import reset_document_store
        
        reset_document_store()
        client = TestClient(app)
        
        # Upload a document
        pdf_content = create_test_pdf()
        upload_response = client.post(
            "/upload",
            files={"file": ("test.pdf", pdf_content, "application/pdf")}
        )
        
        doc_id = upload_response.json()["doc_id"]
        
        # Delete the document
        response = client.delete(f"/document/{doc_id}")
        
        assert response.status_code == 200
        assert response.json()["deleted"] is True

    def test_delete_nonexistent_document(self):
        """Test deleting non-existent document."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.delete("/document/nonexistent123")
        
        assert response.status_code == 404


class TestRateLimiting:
    """Tests for rate limiting functionality."""

    def test_rate_limiter_allows_requests(self):
        """Test that rate limiter allows requests within limit."""
        from app.main import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=10)
        
        # Should allow first 10 requests
        for i in range(10):
            assert limiter.is_allowed("test_client") is True

    def test_rate_limiter_blocks_excess_requests(self):
        """Test that rate limiter blocks requests over limit."""
        from app.main import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=5)
        
        # Use up the limit
        for i in range(5):
            limiter.is_allowed("test_client")
        
        # Next request should be blocked
        assert limiter.is_allowed("test_client") is False

    def test_rate_limiter_tracks_different_clients(self):
        """Test that rate limiter tracks clients separately."""
        from app.main import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=2)
        
        # Use up limit for client1
        limiter.is_allowed("client1")
        limiter.is_allowed("client1")
        assert limiter.is_allowed("client1") is False
        
        # client2 should still be allowed
        assert limiter.is_allowed("client2") is True

    def test_rate_limiter_get_remaining(self):
        """Test getting remaining requests."""
        from app.main import RateLimiter
        
        limiter = RateLimiter(requests_per_minute=10)
        
        # Initial remaining should be 10
        assert limiter.get_remaining("new_client") == 10
        
        # After one request, remaining should be 9
        limiter.is_allowed("new_client")
        assert limiter.get_remaining("new_client") == 9


class TestAPIAuthentication:
    """Tests for API key authentication."""

    def test_auth_not_required_by_default(self):
        """Test that auth is not required by default."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        # Should work without API key
        response = client.get("/health")
        assert response.status_code == 200

    def test_auth_required_when_enabled(self):
        """Test that auth is required when enabled."""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.config import get_settings
        
        settings = get_settings()
        original_require_auth = settings.api.require_auth
        original_api_key = settings.api.api_key
        
        try:
            settings.api.require_auth = True
            settings.api.api_key = "test_secret_key"
            
            client = TestClient(app)
            
            # Upload should fail without API key
            pdf_content = create_test_pdf()
            response = client.post(
                "/upload",
                files={"file": ("test.pdf", pdf_content, "application/pdf")}
            )
            
            assert response.status_code == 401
        finally:
            settings.api.require_auth = original_require_auth
            settings.api.api_key = original_api_key

    def test_auth_with_valid_key(self):
        """Test that valid API key is accepted."""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.config import get_settings
        
        settings = get_settings()
        original_require_auth = settings.api.require_auth
        original_api_key = settings.api.api_key
        
        try:
            settings.api.require_auth = True
            settings.api.api_key = "test_secret_key"
            
            client = TestClient(app)
            
            pdf_content = create_test_pdf()
            response = client.post(
                "/upload",
                files={"file": ("test.pdf", pdf_content, "application/pdf")},
                headers={"X-API-Key": "test_secret_key"}
            )
            
            assert response.status_code == 200
        finally:
            settings.api.require_auth = original_require_auth
            settings.api.api_key = original_api_key

    def test_auth_with_invalid_key(self):
        """Test that invalid API key is rejected."""
        from fastapi.testclient import TestClient
        from app.main import app
        from app.config import get_settings
        
        settings = get_settings()
        original_require_auth = settings.api.require_auth
        original_api_key = settings.api.api_key
        
        try:
            settings.api.require_auth = True
            settings.api.api_key = "correct_key"
            
            client = TestClient(app)
            
            pdf_content = create_test_pdf()
            response = client.post(
                "/upload",
                files={"file": ("test.pdf", pdf_content, "application/pdf")},
                headers={"X-API-Key": "wrong_key"}
            )
            
            assert response.status_code == 403
        finally:
            settings.api.require_auth = original_require_auth
            settings.api.api_key = original_api_key


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self):
        """Test that CORS headers are present."""
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        
        response = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:8501",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # CORS should allow the request
        assert response.status_code in [200, 204]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
