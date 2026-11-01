"""
scanner/sqlite_scanner.py
Safe, modular SQLite Scanner for Personal Data Discovery.
"""

import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
from .detection import PersonalDataDetector, DetectionResult


class SQLiteScanner:
    """
    Scans SQLite databases in read-only mode to discover candidate personal-data fields.
    Guarantees no modifications to source tables.
    """

    def __init__(self, detector: Optional[PersonalDataDetector] = None):
        self.detector = detector or PersonalDataDetector()

    def discover_tables(self, db_path: Union[str, Path]) -> List[str]:
        """
        Discovers all user tables in SQLite database safely.
        """
        path = Path(db_path)
        if not path.exists():
            raise FileNotFoundError(f"SQLite database file not found: {path}")

        # Connect in read-only URI mode to prevent any modification
        uri_path = f"file:{path.resolve().as_posix()}?mode=ro"
        conn = None
        try:
            conn = sqlite3.connect(uri_path, uri=True)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            )
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        finally:
            if conn:
                conn.close()

    def discover_table_columns(self, db_path: Union[str, Path], table_name: str) -> List[str]:
        """
        Retrieves column names for a given table using PRAGMA table_info.
        """
        path = Path(db_path)
        uri_path = f"file:{path.resolve().as_posix()}?mode=ro"
        conn = None
        try:
            conn = sqlite3.connect(uri_path, uri=True)
            cursor = conn.cursor()
            # Escape table name using sqlite quoting
            clean_table = table_name.replace('"', '""')
            cursor.execute(f'PRAGMA table_info("{clean_table}");')
            cols = [row[1] for row in cursor.fetchall()]
            return cols
        finally:
            if conn:
                conn.close()

    def scan_table(
        self,
        db_path: Union[str, Path],
        table_name: str,
        sample_limit: int = 100
    ) -> List[DetectionResult]:
        """
        Samples rows from a table and runs personal data detection on each column.
        """
        path = Path(db_path)
        source_name = path.name
        results: List[DetectionResult] = []

        columns = self.discover_table_columns(path, table_name)
        if not columns:
            return results

        uri_path = f"file:{path.resolve().as_posix()}?mode=ro"
        conn = None
        try:
            conn = sqlite3.connect(uri_path, uri=True)
            cursor = conn.cursor()

            # Quoted identifiers for SQL safety
            escaped_cols = [c.replace('"', '""') for c in columns]
            quoted_cols = ", ".join([f'"{c}"' for c in escaped_cols])
            clean_table = table_name.replace('"', '""')

            # Parameterized limit query
            query = f'SELECT {quoted_cols} FROM "{clean_table}" LIMIT ?;'
            cursor.execute(query, (sample_limit,))
            rows = cursor.fetchall()

            # Organize into column sample lists
            for idx, col_name in enumerate(columns):
                col_samples = [row[idx] for row in rows if row[idx] is not None]
                res = self.detector.evaluate_column(
                    column_name=col_name,
                    sample_values=col_samples,
                    source_name=source_name,
                    table_name=table_name
                )
                results.append(res)

            return results
        finally:
            if conn:
                conn.close()

    def scan_database(
        self,
        db_path: Union[str, Path],
        sample_limit: int = 100
    ) -> List[DetectionResult]:
        """
        Scans all tables in a SQLite database and returns aggregated detection results.
        """
        path = Path(db_path)
        tables = self.discover_tables(path)
        all_results: List[DetectionResult] = []

        for tbl in tables:
            tbl_results = self.scan_table(path, tbl, sample_limit=sample_limit)
            all_results.extend(tbl_results)

        return all_results
