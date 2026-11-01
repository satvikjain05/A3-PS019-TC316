"""
tests/test_detection.py
Unit tests for detection heuristics, pattern matching, confidence scoring, and masking.
"""

import pytest
from scanner.detection import PersonalDataDetector, DetectionResult


@pytest.fixture
def detector():
    return PersonalDataDetector()


def test_email_detection_valid_and_invalid(detector):
    # Valid emails
    assert detector.match_email("aryan@example.com")
    assert detector.match_email("priya.sharma@example.org")
    assert detector.match_email("user123@privacy-test.corp")
    # Invalid emails
    assert not detector.match_email("not-an-email")
    assert not detector.match_email("missing-at-sign.com")
    assert not detector.match_email("user@.com")


def test_phone_detection_indian_formats(detector):
    # Valid Indian formats
    assert detector.match_phone("+91-98200-12345")
    assert detector.match_phone("+91 98450 67890")
    assert detector.match_phone("09810012345")
    assert detector.match_phone("9820012345")
    assert detector.match_phone("8826054321")
    # Invalid numbers
    assert not detector.match_phone("12345")
    assert not detector.match_phone("abcdefghij")
    assert not detector.match_phone("0000000000")


def test_address_detection(detector):
    # Valid synthetic addresses with street, locality, city, state, pin
    addr1 = "Flat 402, Lotus Enclave, MG Road, Indiranagar, Bengaluru, Karnataka - 560001"
    addr2 = "Flat 101, Green Meadows, FC Road, Shivajinagar, Pune, Maharashtra - 411001"
    assert detector.match_address(addr1)
    assert detector.match_address(addr2)
    # Invalid addresses
    assert not detector.match_address("123 Main St")  # Too short / incomplete
    assert not detector.match_address("Bangalore")


def test_government_id_synthetic_markers(detector):
    # Synthetic Aadhaar, PAN, Voter ID
    assert detector.match_govt_id("SYN-AAD-1234-5678-9012")
    assert detector.match_govt_id("SYNPA1234A")
    assert detector.match_govt_id("SYNVOT1234567")
    assert detector.match_govt_id("SYN-DL-TEST-99887")
    # Real numbers or non-synthetic IDs should not match synthetic pattern
    assert not detector.match_govt_id("123456789012")
    assert not detector.match_govt_id("ABCDE1234F")
    assert not detector.match_govt_id("EMP-2001")


def test_name_detection(detector):
    assert detector.match_name("Aarav Sharma")
    assert detector.match_name("Priya Kumar Verma")
    assert detector.match_name("R. K. Narayan")
    # Invalid names
    assert not detector.match_name("john")  # Not capitalized
    assert not detector.match_name("User_123")  # Digits and symbols
    assert not detector.match_name("SingleWord")


def test_evaluate_column_email_header_and_values(detector):
    samples = [
        "aryan@example.com",
        "priya.s@example.org",
        "test.user@privacy-test.corp",
        None,
        "rohan.m@example.net"
    ]
    res = detector.evaluate_column("contact_email", samples, "test.csv")
    assert res.is_personal is True
    assert res.detected_class == "EMAIL"
    assert res.confidence_score >= 0.70
    assert "Header pattern match" in res.evidence_details
    assert len(res.masked_samples) > 0
    assert "@" in res.masked_samples[0]
    assert "***" in res.masked_samples[0]


def test_evaluate_column_negative_header_exclusions(detector):
    # company_name should NOT be classified as NAME even if values are capitalized
    samples = ["Acme Corporation", "Global Logistics", "Apex Solutions", "Alpha Technologies"]
    res = detector.evaluate_column("company_name", samples, "vendors.csv")
    assert res.detected_class != "NAME"
    assert res.is_personal is False


def test_evaluate_column_ambiguous_mixed_tokens(detector):
    # Column with mixed tokens (half emails, half reference tokens) without email header
    samples = [
        "REF-NOTIFY-1001",
        "user1@example.com",
        "REF-NOTIFY-1002",
        "user2@example.com",
        "REF-NOTIFY-1003"
    ]
    res = detector.evaluate_column("contact_pref_token", samples, "customers.csv")
    assert res.is_personal is False
    assert res.is_ambiguous is True or res.detected_class is None


def test_masking_utility(detector):
    # Test that sensitive values are safely masked
    email_masked = detector.mask_value("deepak.sharma@example.com", "EMAIL")
    assert email_masked.startswith("d***")
    assert "@example.com" in email_masked

    phone_masked = detector.mask_value("+91-98200-12345", "PHONE_NUMBER")
    assert "***" in phone_masked
    assert "98200" not in phone_masked

    name_masked = detector.mask_value("Aarav Sharma", "NAME")
    assert name_masked == "A***v S****a"

    govt_masked = detector.mask_value("SYN-AAD-1234-5678-9012", "GOVERNMENT_ID")
    assert "****" in govt_masked
    assert "1234" not in govt_masked
