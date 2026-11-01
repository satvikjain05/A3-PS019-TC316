"""
tests/test_scanner.py
Integration tests for CSVScanner and SQLiteScanner.
"""

import sqlite3
import pytest
from pathlib import Path
from scanner.csv_scanner import CSVScanner
from scanner.sqlite_scanner import SQLiteScanner

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture
def csv_scanner():
    return CSVScanner()


@pytest.fixture
def sqlite_scanner():
    return SQLiteScanner()


def test_csv_scan_customers(csv_scanner):
    csv_path = DATA_DIR / "customers.csv"
    results = csv_scanner.scan_file(csv_path, sample_limit=50)
    assert len(results) > 0

    col_classes = {r.column_name: r.detected_class for r in results}
    assert col_classes.get("full_name") == "NAME"
    assert col_classes.get("email_address") == "EMAIL"
    assert col_classes.get("phone_number") == "PHONE_NUMBER"
    assert col_classes.get("residential_address") == "ADDRESS"
    assert col_classes.get("synthetic_govt_id") == "GOVERNMENT_ID"
    assert col_classes.get("customer_id") is None or col_classes.get("customer_id") == "NOT_PERSONAL"


def test_csv_scan_empty_file(csv_scanner, tmp_path):
    empty_csv = tmp_path / "empty.csv"
    empty_csv.write_text("", encoding="utf-8")
    results = csv_scanner.scan_file(empty_csv)
    assert results == []


def test_csv_scan_missing_file(csv_scanner, tmp_path):
    non_existent = tmp_path / "does_not_exist.csv"
    with pytest.raises(FileNotFoundError):
        csv_scanner.scan_file(non_existent)


def test_csv_scan_malformed_file(csv_scanner, tmp_path):
    # CSV with uneven commas / malformed lines
    malformed_csv = tmp_path / "malformed.csv"
    malformed_csv.write_text(
        "full_name,email_address\n"
        "Aarav Sharma,aarav@example.com\n"
        "Broken row with too many commas,a,b,c,d,e\n"
        "Priya Patel,priya@example.com\n",
        encoding="utf-8"
    )
    results = csv_scanner.scan_file(malformed_csv)
    assert len(results) == 2
    classes = {r.column_name: r.detected_class for r in results}
    assert classes.get("full_name") == "NAME"
    assert classes.get("email_address") == "EMAIL"


def test_sqlite_table_discovery(sqlite_scanner):
    db_path = DATA_DIR / "privacy_demo.db"
    tables = sqlite_scanner.discover_tables(db_path)
    assert "customers" in tables
    assert "employees" in tables
    assert "support_tickets" in tables
    assert "system_logs" in tables


def test_sqlite_column_discovery(sqlite_scanner):
    db_path = DATA_DIR / "privacy_demo.db"
    cols = sqlite_scanner.discover_table_columns(db_path, "customers")
    assert "full_name" in cols
    assert "email_address" in cols
    assert "customer_id" in cols


def test_sqlite_scan_database_read_only(sqlite_scanner):
    db_path = DATA_DIR / "privacy_demo.db"
    results = sqlite_scanner.scan_database(db_path, sample_limit=50)
    assert len(results) > 0

    # Ensure no rows were modified in database
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM customers;")
    count = cur.fetchone()[0]
    conn.close()
    assert count == 120  # Original generated count preserved exactly
