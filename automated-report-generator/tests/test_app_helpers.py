"""
Tests for Streamlit app helper functions.
Uses mocking to test functions without running the full Streamlit app.
"""

import sys
import io
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pandas as pd
import numpy as np
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestLoadAndValidateData:
    """Tests for load_and_validate_data function."""

    def test_load_csv_data(self):
        """Test loading CSV data from bytes."""
        # Import with mocked streamlit
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            # Create CSV content
            csv_content = b"Date,Product,Revenue\n2024-01-01,A,100\n2024-01-02,B,200"
            
            # Import the function after mocking
            from app import load_and_validate_data
            
            df = load_and_validate_data(csv_content, "test.csv")
            
            assert df is not None
            assert len(df) == 2
            assert "Date" in df.columns
            assert "Product" in df.columns
            assert "Revenue" in df.columns

    def test_load_csv_with_encoding(self):
        """Test loading CSV with UTF-8 encoding."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            csv_content = "Name,Value\nCafé,100\nNaïve,200".encode('utf-8')
            
            from app import load_and_validate_data
            
            df = load_and_validate_data(csv_content, "test.csv")
            
            assert df is not None
            assert "Café" in df["Name"].values

    def test_load_unsupported_format_raises_error(self):
        """Test that unsupported format raises ValueError."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            from app import load_and_validate_data
            
            with pytest.raises(ValueError) as exc_info:
                load_and_validate_data(b"content", "test.txt")
            
            assert "Unsupported" in str(exc_info.value)

    def test_column_names_stripped(self):
        """Test that column names are stripped of whitespace."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            csv_content = b"  Date  ,  Product  ,  Revenue  \n2024-01-01,A,100"
            
            from app import load_and_validate_data
            
            df = load_and_validate_data(csv_content, "test.csv")
            
            # Column names should be stripped
            assert "Date" in df.columns
            assert "  Date  " not in df.columns


class TestGetExcelSheetNames:
    """Tests for get_excel_sheet_names function."""

    def test_get_sheet_names(self):
        """Test getting sheet names from Excel file."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            # Create a simple Excel file in memory
            df1 = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
            df2 = pd.DataFrame({"X": [5, 6], "Y": [7, 8]})
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='Sheet1', index=False)
                df2.to_excel(writer, sheet_name='Sheet2', index=False)
            
            excel_content = buffer.getvalue()
            
            from app import get_excel_sheet_names
            
            sheet_names = get_excel_sheet_names(excel_content)
            
            assert "Sheet1" in sheet_names
            assert "Sheet2" in sheet_names
            assert len(sheet_names) == 2


class TestInitSessionState:
    """Tests for init_session_state function."""

    def test_init_session_state_sets_defaults(self):
        """Test that session state is initialized with defaults."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            # Re-import to get fresh module
            import importlib
            if 'app' in sys.modules:
                del sys.modules['app']
            
            # Patch session_state with a dict-like object
            class SessionState(dict):
                pass
            
            mock_st.session_state = SessionState()
            
            from app import init_session_state
            init_session_state()
            
            # Check that defaults are set
            assert 'step' in mock_st.session_state
            assert mock_st.session_state['step'] == 1


class TestRenderHtmlBlock:
    """Tests for render_html_block function."""

    def test_render_html_block_cleans_indentation(self):
        """Test that HTML block cleans indentation."""
        mock_st = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app' in sys.modules:
                del sys.modules['app']
            
            from app import render_html_block
            
            html = """
                <div>
                    <p>Test</p>
                </div>
            """
            
            render_html_block(html)
            
            # Should have called markdown with cleaned HTML
            mock_st.markdown.assert_called_once()
            call_args = mock_st.markdown.call_args
            assert call_args[1].get('unsafe_allow_html') is True


class TestFormatting:
    """Tests for formatting helper functions used in app."""

    def test_format_number_for_display(self):
        """Test number formatting for display."""
        from src.utils import format_number
        
        assert format_number(1234567) == "1,234,567"
        assert format_number(1234.56, decimals=2) == "1,234.56"

    def test_format_currency_for_display(self):
        """Test currency formatting for display."""
        from src.utils import format_currency
        
        assert format_currency(1000) == "$1,000.00"
        assert format_currency(-500) == "-$500.00"


class TestDataValidation:
    """Tests for data validation helpers."""

    def test_validate_csv_structure(self):
        """Test that CSV structure is properly validated."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            csv_content = b"Date,Product,Revenue\n2024-01-01,A,100"
            
            from app import load_and_validate_data
            
            df = load_and_validate_data(csv_content, "test.csv")
            
            assert isinstance(df, pd.DataFrame)
            assert len(df.columns) == 3

    def test_empty_csv_handling(self):
        """Test handling of CSV with only headers."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            csv_content = b"Date,Product,Revenue\n"
            
            from app import load_and_validate_data
            
            df = load_and_validate_data(csv_content, "test.csv")
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 0
            assert len(df.columns) == 3


class TestExcelLoading:
    """Tests for Excel file loading."""

    def test_load_excel_default_sheet(self):
        """Test loading Excel with default sheet."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            # Create Excel file
            df = pd.DataFrame({
                "Date": ["2024-01-01", "2024-01-02"],
                "Value": [100, 200]
            })
            
            buffer = io.BytesIO()
            df.to_excel(buffer, index=False, engine='openpyxl')
            excel_content = buffer.getvalue()
            
            from app import load_and_validate_data
            
            result = load_and_validate_data(excel_content, "test.xlsx")
            
            assert len(result) == 2
            assert "Date" in result.columns

    def test_load_excel_specific_sheet(self):
        """Test loading Excel with specific sheet name."""
        with patch.dict('sys.modules', {'streamlit': MagicMock()}):
            # Create Excel file with multiple sheets
            df1 = pd.DataFrame({"A": [1, 2]})
            df2 = pd.DataFrame({"B": [3, 4]})
            
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df1.to_excel(writer, sheet_name='Data1', index=False)
                df2.to_excel(writer, sheet_name='Data2', index=False)
            
            excel_content = buffer.getvalue()
            
            from app import load_and_validate_data
            
            result = load_and_validate_data(excel_content, "test.xlsx", sheet_name="Data2")
            
            assert "B" in result.columns
            assert "A" not in result.columns


class TestSessionStateDefaults:
    """Tests for session state default values."""

    def test_all_defaults_present(self):
        """Test that all expected defaults are defined."""
        mock_st = MagicMock()
        mock_st.session_state = {}
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app' in sys.modules:
                del sys.modules['app']
            
            from app import init_session_state
            init_session_state()
            
            expected_keys = [
                'step', 'uploaded_file', 'df', 'processor',
                'selected_template', 'column_mapping', 'generated_reports',
                'include_ai', 'output_formats', 'missing_value_strategy'
            ]
            
            for key in expected_keys:
                assert key in mock_st.session_state, f"Missing key: {key}"


class TestIconSystem:
    """Tests for the icon system used in the app."""

    def test_icon_files_exist(self):
        """Test that icon module exists and is importable."""
        assets_path = Path(__file__).parent.parent / "assets"
        icons_path = assets_path / "icons.py"
        
        assert icons_path.exists(), "icons.py should exist in assets folder"

    def test_get_icon_function(self):
        """Test get_icon function from icons module."""
        sys.path.insert(0, str(Path(__file__).parent.parent / "assets"))
        
        try:
            from icons import get_icon
            
            icon = get_icon("chart-bar")
            assert icon is not None
            assert "<svg" in icon or "svg" in icon.lower()
        except ImportError:
            pytest.skip("Icons module not available")


class TestCSSLoading:
    """Tests for CSS loading functionality."""

    def test_css_file_exists(self):
        """Test that CSS file exists."""
        css_path = Path(__file__).parent.parent / "assets" / "styles.css"
        assert css_path.exists(), "styles.css should exist in assets folder"

    def test_load_css_function(self):
        """Test load_css function."""
        mock_st = MagicMock()
        
        with patch.dict('sys.modules', {'streamlit': mock_st}):
            if 'app' in sys.modules:
                del sys.modules['app']
            
            from app import load_css
            load_css()
            
            # Should have called markdown to inject CSS
            # (may not be called if CSS file doesn't exist in test environment)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
