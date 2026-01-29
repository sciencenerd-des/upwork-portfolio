"""
Tests for Streamlit app helper functions in Document Intelligence.
Tests confidence formatting, icon handling, and session state.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestConfidenceFormatting:
    """Tests for confidence formatting functions."""

    def test_get_confidence_class_high(self):
        """Test high confidence class."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(0.95)
            assert result == "confidence-high"

    def test_get_confidence_class_medium(self):
        """Test medium confidence class."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(0.85)
            assert result == "confidence-medium"

    def test_get_confidence_class_low(self):
        """Test low confidence class."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(0.65)
            assert result == "confidence-low"

    def test_get_confidence_class_none(self):
        """Test confidence class with None value."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(None)
            assert result == "confidence-low"

    def test_format_confidence_high(self):
        """Test formatting high confidence."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import format_confidence
            
            result = format_confidence(0.95)
            assert "confidence-high" in result
            assert "95%" in result

    def test_format_confidence_medium(self):
        """Test formatting medium confidence."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import format_confidence
            
            result = format_confidence(0.80)
            assert "confidence-medium" in result
            assert "80%" in result

    def test_format_confidence_low(self):
        """Test formatting low confidence."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import format_confidence
            
            result = format_confidence(0.50)
            assert "confidence-low" in result
            assert "50%" in result

    def test_format_confidence_none(self):
        """Test formatting None confidence."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import format_confidence
            
            result = format_confidence(None)
            assert "N/A" in result
            assert "confidence-low" in result

    def test_format_confidence_boundary_high(self):
        """Test confidence at high boundary."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(0.90)
            assert result == "confidence-high"

    def test_format_confidence_boundary_medium(self):
        """Test confidence at medium boundary."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_confidence_class
            
            result = get_confidence_class(0.75)
            assert result == "confidence-medium"


class TestIconSystem:
    """Tests for icon handling."""

    def test_get_icon_returns_svg(self):
        """Test get_icon returns SVG content."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_icon
            
            result = get_icon("document")
            assert "<svg" in result

    def test_get_icon_with_size(self):
        """Test get_icon with custom size."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_icon
            
            result = get_icon("sparkles", size=32)
            assert 'width="32"' in result
            assert 'height="32"' in result

    def test_get_icon_fallback(self):
        """Test get_icon returns fallback for unknown icon."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app.streamlit_app import get_icon
            
            result = get_icon("nonexistent_icon")
            # Should return document icon as fallback
            assert "<svg" in result


class TestRenderHtml:
    """Tests for HTML rendering helper."""

    def test_render_html_cleans_indentation(self):
        """Test render_html cleans indentation."""
        mock_st = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app.streamlit_app' in sys.modules:
                del sys.modules['app.streamlit_app']
            
            from app.streamlit_app import render_html
            
            html = """
                <div>
                    <p>Test</p>
                </div>
            """
            
            render_html(html)
            
            mock_st.markdown.assert_called_once()
            call_args = mock_st.markdown.call_args
            assert call_args[1].get('unsafe_allow_html') is True


class TestSessionState:
    """Tests for session state initialization."""

    def test_initialize_session_state(self):
        """Test session state initialization."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app.streamlit_app' in sys.modules:
                del sys.modules['app.streamlit_app']
            
            from app.streamlit_app import initialize_session_state
            
            initialize_session_state()
            
            # Check expected keys are set
            assert 'current_doc_id' in mock_st.session_state
            assert 'conversation_history' in mock_st.session_state

    def test_session_state_preserves_existing(self):
        """Test that existing session state values are preserved."""
        mock_st = MagicMock()
        mock_st.session_state = {'current_doc_id': 'existing_id'}
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app.streamlit_app' in sys.modules:
                del sys.modules['app.streamlit_app']
            
            from app.streamlit_app import initialize_session_state
            
            initialize_session_state()
            
            # Existing value should be preserved
            assert mock_st.session_state['current_doc_id'] == 'existing_id'


class TestCSSLoading:
    """Tests for CSS loading functionality."""

    def test_css_file_exists(self):
        """Test that CSS file exists."""
        css_path = PROJECT_ROOT / "app" / "assets" / "styles.css"
        assert css_path.exists(), f"CSS file should exist at {css_path}"

    def test_load_css(self):
        """Test load_css function."""
        mock_st = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app.streamlit_app' in sys.modules:
                del sys.modules['app.streamlit_app']
            
            from app.streamlit_app import load_css
            
            load_css()
            
            # Should call markdown to inject CSS
            if (PROJECT_ROOT / "app" / "assets" / "styles.css").exists():
                mock_st.markdown.assert_called()


class TestProcessDocument:
    """Tests for document processing function."""

    def test_process_document_validation_failure(self):
        """Test process_document handles validation failure."""
        mock_st = MagicMock()
        mock_st.error = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app.streamlit_app' in sys.modules:
                del sys.modules['app.streamlit_app']
            
            from app.streamlit_app import process_document
            from src.document_loader import DocumentLoader
            
            # Mock validation to fail
            with patch.object(DocumentLoader, 'validate_file') as mock_validate:
                mock_result = MagicMock()
                mock_result.is_valid = False
                mock_result.error_message = "Invalid file"
                mock_validate.return_value = mock_result
                
                result = process_document(b"invalid content", "test.pdf")
                
                # Should return None on validation failure
                assert result is None


class TestEntityDisplay:
    """Tests for entity display helpers."""

    def test_entity_card_rendering(self):
        """Test that entity cards are rendered properly."""
        mock_st = MagicMock()
        mock_st.session_state = {'current_doc_id': None}
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            # Entity display is handled in render_entities_tab
            # Testing the confidence formatting which is used in entity cards
            from app.streamlit_app import format_confidence
            
            result = format_confidence(0.85)
            
            assert "span" in result
            assert "confidence" in result


class TestDocumentStatus:
    """Tests for document status handling."""

    def test_status_enum_values(self):
        """Test DocumentStatus enum values are accessible."""
        from app.models import DocumentStatus
        
        assert DocumentStatus.PENDING.value == "pending"
        assert DocumentStatus.PROCESSING.value == "processing"
        assert DocumentStatus.COMPLETED.value == "completed"
        assert DocumentStatus.FAILED.value == "failed"


class TestExportFormat:
    """Tests for export format handling."""

    def test_export_format_enum_values(self):
        """Test ExportFormat enum values are accessible."""
        from app.models import ExportFormat
        
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.CSV.value == "csv"
        assert ExportFormat.EXCEL.value == "excel"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
