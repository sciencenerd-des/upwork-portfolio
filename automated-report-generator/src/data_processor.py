"""
Data Processor Module for the Automated Report Generator.

This module handles:
- Loading CSV and Excel files
- Data validation and cleaning
- Column type detection and inference
- Column mapping to template requirements
- Missing value handling
"""

import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime
import pandas as pd
import numpy as np

from .utils import (
    load_config,
    get_templates_config,
    parse_date,
    detect_date_column,
    detect_numeric_column,
    clean_numeric_value,
)


class DataValidationError(Exception):
    """Exception raised for data validation errors."""
    pass


class DataProcessor:
    """
    Handles data loading, validation, and processing for report generation.

    Attributes:
        df: The loaded pandas DataFrame
        template_config: Configuration for the selected template
        column_mapping: Mapping of data columns to template fields
    """

    def __init__(self):
        """Initialize the DataProcessor."""
        self.df: Optional[pd.DataFrame] = None
        self.template_config: Optional[Dict] = None
        self.column_mapping: Dict[str, str] = {}
        self.validation_errors: List[str] = []
        self.validation_warnings: List[str] = []
        self._templates_config = get_templates_config()
        self._settings = self._templates_config.get("settings", {})

    def load_file(
        self,
        file_path: Union[str, Path, io.BytesIO],
        file_name: Optional[str] = None,
        sheet_name: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Load data from a CSV or Excel file.

        Args:
            file_path: Path to the file or file-like object
            file_name: Original filename (required for file-like objects)
            sheet_name: Sheet name for Excel files (optional)

        Returns:
            Loaded DataFrame

        Raises:
            DataValidationError: If the file cannot be loaded or is invalid
        """
        self.validation_errors = []
        self.validation_warnings = []

        # Determine file extension
        if isinstance(file_path, (str, Path)):
            file_path = Path(file_path)
            extension = file_path.suffix.lower()
            file_name = file_path.name
        else:
            if file_name is None:
                raise DataValidationError("file_name is required for file-like objects")
            extension = Path(file_name).suffix.lower()

        # Validate file format
        supported_formats = self._settings.get("supported_formats", [".csv", ".xlsx", ".xls"])
        if extension not in supported_formats:
            raise DataValidationError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {', '.join(supported_formats)}"
            )

        try:
            if extension == ".csv":
                self.df = pd.read_csv(file_path, encoding="utf-8")
            elif extension in [".xlsx", ".xls"]:
                if sheet_name:
                    self.df = pd.read_excel(file_path, sheet_name=sheet_name)
                else:
                    self.df = pd.read_excel(file_path)
        except Exception as e:
            raise DataValidationError(f"Error loading file: {str(e)}")

        # Validate row count
        max_rows = self._settings.get("max_rows", 100000)
        if len(self.df) > max_rows:
            raise DataValidationError(
                f"File contains {len(self.df)} rows, exceeding the maximum of {max_rows}"
            )

        if len(self.df) == 0:
            raise DataValidationError("File is empty or contains no data rows")

        # Clean column names
        self.df.columns = [str(col).strip() for col in self.df.columns]

        return self.df

    def load_multiple_files(
        self,
        file_paths: List[Union[str, Path, io.BytesIO]],
        file_names: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        Load and concatenate multiple CSV or Excel files.

        All files must have compatible column structures. Files are stacked
        vertically (rows concatenated).

        Args:
            file_paths: List of paths to files or file-like objects
            file_names: List of original filenames (required for file-like objects)

        Returns:
            Combined DataFrame

        Raises:
            DataValidationError: If files cannot be loaded or have incompatible structures
        """
        if not file_paths:
            raise DataValidationError("No files provided")

        if len(file_paths) == 1:
            # Single file - use regular load
            name = file_names[0] if file_names else None
            return self.load_file(file_paths[0], file_name=name)

        dataframes = []
        column_sets = []

        for i, file_path in enumerate(file_paths):
            file_name = file_names[i] if file_names and i < len(file_names) else None

            # Determine file extension
            if isinstance(file_path, (str, Path)):
                file_path = Path(file_path)
                extension = file_path.suffix.lower()
                file_name = file_path.name
            else:
                if file_name is None:
                    raise DataValidationError(f"file_name is required for file-like object at index {i}")
                extension = Path(file_name).suffix.lower()

            # Validate file format
            supported_formats = self._settings.get("supported_formats", [".csv", ".xlsx", ".xls"])
            if extension not in supported_formats:
                raise DataValidationError(
                    f"Unsupported file format for '{file_name}': {extension}. "
                    f"Supported formats: {', '.join(supported_formats)}"
                )

            try:
                if extension == ".csv":
                    df = pd.read_csv(file_path, encoding="utf-8")
                elif extension in [".xlsx", ".xls"]:
                    df = pd.read_excel(file_path)
            except Exception as e:
                raise DataValidationError(f"Error loading file '{file_name}': {str(e)}")

            if len(df) == 0:
                self.validation_warnings.append(f"File '{file_name}' is empty and was skipped")
                continue

            # Clean column names
            df.columns = [str(col).strip() for col in df.columns]

            # Track columns for compatibility check
            column_sets.append(set(df.columns))
            dataframes.append(df)

        if not dataframes:
            raise DataValidationError("All files were empty")

        # Check column compatibility
        first_columns = column_sets[0]
        for i, cols in enumerate(column_sets[1:], start=2):
            if cols != first_columns:
                missing = first_columns - cols
                extra = cols - first_columns
                warnings = []
                if missing:
                    warnings.append(f"missing columns: {missing}")
                if extra:
                    warnings.append(f"extra columns: {extra}")
                self.validation_warnings.append(
                    f"File {i} has different columns ({', '.join(warnings)}). "
                    "Data will be merged with missing values where needed."
                )

        # Concatenate all dataframes
        self.df = pd.concat(dataframes, ignore_index=True)

        # Validate total row count
        max_rows = self._settings.get("max_rows", 500000)
        if len(self.df) > max_rows:
            raise DataValidationError(
                f"Combined data contains {len(self.df)} rows, exceeding the maximum of {max_rows}"
            )

        return self.df

    def get_excel_sheets(self, file_path: Union[str, Path, io.BytesIO]) -> List[str]:
        """
        Get list of sheet names from an Excel file.

        Args:
            file_path: Path to the Excel file

        Returns:
            List of sheet names
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise DataValidationError(f"Error reading Excel sheets: {str(e)}")

    def detect_column_types(self) -> Dict[str, str]:
        """
        Detect the data type of each column.

        Returns:
            Dictionary mapping column names to detected types
        """
        if self.df is None:
            raise DataValidationError("No data loaded. Call load_file first.")

        column_types = {}

        for col in self.df.columns:
            values = self.df[col].dropna().tolist()

            if len(values) == 0:
                column_types[col] = "empty"
            elif detect_date_column(values):
                column_types[col] = "datetime"
            elif detect_numeric_column(values):
                column_types[col] = "numeric"
            else:
                column_types[col] = "string"

        return column_types

    def suggest_template(self) -> Tuple[str, float]:
        """
        Suggest the best matching template based on column names.

        Returns:
            Tuple of (template_name, confidence_score)
        """
        if self.df is None:
            raise DataValidationError("No data loaded. Call load_file first.")

        templates = self._templates_config.get("templates", {})
        best_template = None
        best_score = 0

        columns_lower = [col.lower() for col in self.df.columns]

        for template_name, template_config in templates.items():
            required = template_config.get("required_columns", {})
            optional = template_config.get("optional_columns", {})

            # Calculate match score
            required_matches = 0
            optional_matches = 0

            for field_name, field_config in required.items():
                aliases = [a.lower() for a in field_config.get("aliases", [])]
                if any(alias in columns_lower or alias == col for col in columns_lower for alias in aliases):
                    required_matches += 1

            for field_name, field_config in optional.items():
                aliases = [a.lower() for a in field_config.get("aliases", [])]
                if any(alias in columns_lower or alias == col for col in columns_lower for alias in aliases):
                    optional_matches += 1

            # Score: required matches weighted more heavily
            total_required = len(required)
            total_optional = len(optional)

            if total_required > 0:
                score = (required_matches / total_required) * 0.8
                if total_optional > 0:
                    score += (optional_matches / total_optional) * 0.2
            else:
                score = 0

            if score > best_score:
                best_score = score
                best_template = template_name

        return best_template, best_score

    def set_template(self, template_name: str) -> None:
        """
        Set the template for report generation.

        Args:
            template_name: Name of the template to use

        Raises:
            DataValidationError: If the template doesn't exist
        """
        templates = self._templates_config.get("templates", {})

        if template_name not in templates:
            available = ", ".join(templates.keys())
            raise DataValidationError(
                f"Template '{template_name}' not found. Available templates: {available}"
            )

        self.template_config = templates[template_name]

    def auto_map_columns(self) -> Dict[str, Optional[str]]:
        """
        Automatically map data columns to template fields.

        Returns:
            Dictionary mapping template fields to data column names
        """
        if self.df is None:
            raise DataValidationError("No data loaded. Call load_file first.")
        if self.template_config is None:
            raise DataValidationError("No template set. Call set_template first.")

        mapping = {}
        columns_lower = {col.lower(): col for col in self.df.columns}

        # Map required columns
        for field_name, field_config in self.template_config.get("required_columns", {}).items():
            aliases = field_config.get("aliases", [])
            mapped_col = None

            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in columns_lower:
                    mapped_col = columns_lower[alias_lower]
                    break

            mapping[field_name] = mapped_col

        # Map optional columns
        for field_name, field_config in self.template_config.get("optional_columns", {}).items():
            aliases = field_config.get("aliases", [])
            mapped_col = None

            for alias in aliases:
                alias_lower = alias.lower()
                if alias_lower in columns_lower:
                    mapped_col = columns_lower[alias_lower]
                    break

            mapping[field_name] = mapped_col

        self.column_mapping = mapping
        return mapping

    def set_column_mapping(self, mapping: Dict[str, str]) -> None:
        """
        Manually set the column mapping.

        Args:
            mapping: Dictionary mapping template fields to data column names
        """
        self.column_mapping = mapping

    def validate_mapping(self) -> Tuple[bool, List[str], List[str]]:
        """
        Validate the current column mapping against template requirements.

        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        if self.template_config is None:
            return False, ["No template set"], []

        errors = []
        warnings = []

        # Check required columns
        for field_name in self.template_config.get("required_columns", {}):
            if field_name not in self.column_mapping or self.column_mapping[field_name] is None:
                errors.append(f"Required field '{field_name}' is not mapped")

        # Check optional columns
        for field_name in self.template_config.get("optional_columns", {}):
            if field_name not in self.column_mapping or self.column_mapping[field_name] is None:
                warnings.append(f"Optional field '{field_name}' is not mapped")

        self.validation_errors = errors
        self.validation_warnings = warnings

        return len(errors) == 0, errors, warnings

    def process_data(self) -> pd.DataFrame:
        """
        Process the data according to the template requirements.

        This includes:
        - Converting date columns to datetime
        - Converting numeric columns to float
        - Handling missing values
        - Validating data types

        Returns:
            Processed DataFrame

        Raises:
            DataValidationError: If processing fails
        """
        if self.df is None:
            raise DataValidationError("No data loaded")
        if self.template_config is None:
            raise DataValidationError("No template set")

        # Work on a copy
        processed_df = self.df.copy()

        # Process required columns
        all_columns = {
            **self.template_config.get("required_columns", {}),
            **self.template_config.get("optional_columns", {})
        }

        for field_name, field_config in all_columns.items():
            if field_name not in self.column_mapping or self.column_mapping[field_name] is None:
                continue

            col_name = self.column_mapping[field_name]
            expected_type = field_config.get("type", "string")

            if col_name not in processed_df.columns:
                continue

            try:
                if expected_type == "datetime":
                    processed_df[col_name] = pd.to_datetime(
                        processed_df[col_name],
                        errors="coerce"
                    )
                elif expected_type == "numeric":
                    processed_df[col_name] = processed_df[col_name].apply(clean_numeric_value)
                # String columns are left as-is
            except Exception as e:
                self.validation_warnings.append(
                    f"Could not convert column '{col_name}' to {expected_type}: {str(e)}"
                )

        self.df = processed_df
        return processed_df

    def get_preview(self, n_rows: int = 10) -> pd.DataFrame:
        """
        Get a preview of the loaded data.

        Args:
            n_rows: Number of rows to include in preview

        Returns:
            DataFrame with first n_rows
        """
        if self.df is None:
            raise DataValidationError("No data loaded")

        return self.df.head(n_rows)

    def get_column_stats(self, column: str) -> Dict[str, Any]:
        """
        Get statistics for a specific column.

        Args:
            column: Column name

        Returns:
            Dictionary of statistics
        """
        if self.df is None:
            raise DataValidationError("No data loaded")

        if column not in self.df.columns:
            raise DataValidationError(f"Column '{column}' not found")

        col_data = self.df[column]
        stats = {
            "count": len(col_data),
            "null_count": col_data.isnull().sum(),
            "null_percentage": (col_data.isnull().sum() / len(col_data)) * 100,
            "unique_count": col_data.nunique(),
        }

        if pd.api.types.is_numeric_dtype(col_data):
            stats.update({
                "min": col_data.min(),
                "max": col_data.max(),
                "mean": col_data.mean(),
                "median": col_data.median(),
                "std": col_data.std(),
            })
        elif pd.api.types.is_datetime64_any_dtype(col_data):
            stats.update({
                "min": col_data.min(),
                "max": col_data.max(),
                "range_days": (col_data.max() - col_data.min()).days if col_data.notna().any() else 0,
            })
        else:
            # String/categorical
            stats.update({
                "top_values": col_data.value_counts().head(5).to_dict(),
            })

        return stats

    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the entire dataset.

        Returns:
            Dictionary of summary statistics
        """
        if self.df is None:
            raise DataValidationError("No data loaded")

        return {
            "row_count": len(self.df),
            "column_count": len(self.df.columns),
            "columns": list(self.df.columns),
            "memory_usage_mb": self.df.memory_usage(deep=True).sum() / (1024 * 1024),
            "null_counts": self.df.isnull().sum().to_dict(),
            "dtypes": {col: str(dtype) for col, dtype in self.df.dtypes.items()},
        }

    def get_mapped_data(self) -> Dict[str, pd.Series]:
        """
        Get the data with standardized field names based on mapping.

        Returns:
            Dictionary mapping field names to data series
        """
        if self.df is None:
            raise DataValidationError("No data loaded")

        result = {}
        for field_name, col_name in self.column_mapping.items():
            if col_name and col_name in self.df.columns:
                result[field_name] = self.df[col_name]

        return result

    def get_date_range(self) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Get the date range from the date column.

        Returns:
            Tuple of (start_date, end_date)
        """
        date_col = self.column_mapping.get("date")
        if not date_col or date_col not in self.df.columns:
            return None, None

        dates = pd.to_datetime(self.df[date_col], errors="coerce")
        valid_dates = dates.dropna()

        if len(valid_dates) == 0:
            return None, None

        return valid_dates.min().to_pydatetime(), valid_dates.max().to_pydatetime()

    def fill_missing_values(self, strategy: str = "drop") -> pd.DataFrame:
        """
        Handle missing values in the data.

        Args:
            strategy: How to handle missing values:
                - "drop": Drop rows with missing values
                - "zero": Fill numeric columns with 0
                - "mean": Fill numeric columns with mean
                - "forward": Forward fill

        Returns:
            DataFrame with missing values handled
        """
        if self.df is None:
            raise DataValidationError("No data loaded")

        if strategy == "drop":
            self.df = self.df.dropna()
        elif strategy == "zero":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(0)
        elif strategy == "mean":
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
        elif strategy == "forward":
            self.df = self.df.fillna(method="ffill")

        return self.df
