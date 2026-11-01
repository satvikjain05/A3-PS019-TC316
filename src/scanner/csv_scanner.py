"""
scanner/csv_scanner.py
Safe, modular CSV Scanner for Personal Data Discovery.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
import pandas as pd
from .detection import PersonalDataDetector, DetectionResult


class CSVScanner:
    """
    Scans CSV files to discover candidate personal-data fields.
    Does not modify or delete source files.
    """

    def __init__(self, detector: Optional[PersonalDataDetector] = None, max_file_size_mb: int = 25):
        self.detector = detector or PersonalDataDetector()
        self.max_file_size_bytes = max_file_size_mb * 1024 * 1024

    def scan_file(
        self,
        filepath_or_buffer: Union[str, Path, object],
        filename: str = "",
        sample_limit: int = 100
    ) -> List[DetectionResult]:
        """
        Scans a CSV file (given as path or file-like buffer) and returns detection results per column.
        """
        results: List[DetectionResult] = []

        # Determine source name
        if isinstance(filepath_or_buffer, (str, Path)):
            path = Path(filepath_or_buffer)
            source_name = filename or path.name

            # Safe validation: check file exists and size
            if not path.exists():
                raise FileNotFoundError(f"Source CSV file not found: {path}")

            if path.stat().st_size > self.max_file_size_bytes:
                raise ValueError(f"File size exceeds maximum allowed safety limit ({self.max_file_size_bytes // (1024*1024)} MB).")

            if path.stat().st_size == 0:
                # Handle empty file gracefully
                return results

            # Attempt reading with fallback encodings
            df = None
            for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
                try:
                    df = pd.read_csv(
                        path,
                        nrows=sample_limit if sample_limit > 0 else None,
                        encoding=encoding,
                        on_bad_lines="skip"
                    )
                    break
                except Exception:
                    continue

            if df is None:
                raise ValueError(f"Could not parse CSV file '{source_name}' with supported encodings.")

        else:
            # File-like object (e.g. Streamlit uploaded file)
            source_name = filename or "uploaded_file.csv"
            try:
                # Reset pointer if possible
                if hasattr(filepath_or_buffer, "seek"):
                    filepath_or_buffer.seek(0)
                df = pd.read_csv(
                    filepath_or_buffer,
                    nrows=sample_limit if sample_limit > 0 else None,
                    on_bad_lines="skip"
                )
            except Exception as e:
                raise ValueError(f"Failed to read uploaded CSV data: {str(e)}")

        if df is None or df.empty or len(df.columns) == 0:
            return results

        # Evaluate each column safely
        for col in df.columns:
            col_name = str(col).strip()
            # Extract sample values, dropping nulls/nans for detection
            sample_vals = df[col].dropna().tolist()
            res = self.detector.evaluate_column(
                column_name=col_name,
                sample_values=sample_vals,
                source_name=source_name,
                table_name=""
            )
            results.append(res)

        return results
