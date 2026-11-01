"""
scanner/detection.py
Core Pattern Recognition, Heuristics, Confidence Scoring, and Value Masking.

Supported Classes:
- NAME
- EMAIL
- PHONE_NUMBER
- ADDRESS
- GOVERNMENT_ID
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


@dataclass
class DetectionResult:
    """Represents the discovery evaluation result for a single dataset column."""
    source_name: str
    table_name: str
    column_name: str
    detected_class: Optional[str]  # NAME, EMAIL, PHONE_NUMBER, ADDRESS, GOVERNMENT_ID or None
    is_personal: bool
    confidence_score: float        # Heuristic score [0.0, 1.0]
    header_matched: Optional[str]
    sample_count: int
    non_null_count: int
    matching_sample_count: int
    sample_match_rate: float
    masked_samples: List[str] = field(default_factory=list)
    evidence_details: str = ""
    is_ambiguous: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_name": self.source_name,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "detected_class": self.detected_class or "NOT_PERSONAL",
            "is_personal": self.is_personal,
            "confidence_score": round(self.confidence_score, 2),
            "header_matched": self.header_matched or "None",
            "sample_count": self.sample_count,
            "non_null_count": self.non_null_count,
            "matching_sample_count": self.matching_sample_count,
            "sample_match_rate": round(self.sample_match_rate, 4),
            "masked_samples": ", ".join(self.masked_samples[:3]),
            "evidence_details": self.evidence_details,
            "is_ambiguous": self.is_ambiguous,
            "notes": self.notes
        }


class PersonalDataDetector:
    """
    Rule-based and heuristic scanner engine that analyzes column names and sampled values
    to discover personal data candidates across five predefined classes.
    """

    # 1. Regex patterns for value validation
    EMAIL_REGEX = re.compile(
        r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
        re.IGNORECASE
    )

    # Indian phone formats: +91-XXXXX-XXXXX, +91 XXXXXXXXXX, 0XXXXXXXXXX, 9XXXXXXXXX, 10 digits
    PHONE_REGEX = re.compile(
        r"^(?:\+91[\-\s]?)?[0]?[6-9]\d{4}[\-\s]?\d{5}$|^(?:\+91[\-\s]?)?[0]?[6-9]\d{9}$",
        re.IGNORECASE
    )

    # Address indicators
    ADDRESS_KEYWORDS = [
        "street", "st.", "st ", "road", "rd.", "rd ", "avenue", "ave.", "ave ",
        "lane", "flat", "apt", "apartment", "block", "sector", "residency",
        "towers", "heights", "enclave", "colony", "nagar", "marg", "layout",
        "post", "pin", "pune", "mumbai", "delhi", "bengaluru", "chennai", "kolkata",
        "hyderabad", "karnataka", "maharashtra", "tamil nadu", "gujarat"
    ]
    INDIAN_PIN_REGEX = re.compile(r"\b[1-9][0-9]{5}\b")

    # Synthetic Government IDs (Strictly synthetic markers)
    SYN_AADHAAR_REGEX = re.compile(r"^SYN-AAD-\d{4}-\d{4}-\d{4}$", re.IGNORECASE)
    SYN_PAN_REGEX = re.compile(r"^SYNPA\d{4}[A-Z]$|^TESTP\d{4}[A-Z]$", re.IGNORECASE)
    SYN_VOTER_REGEX = re.compile(r"^SYNVOT\d{6,8}$", re.IGNORECASE)
    SYN_GENERIC_GOVT_REGEX = re.compile(r"^(?:SYN|TEST|DUMMY)-(?:ID|DL|SSN|UID|PASSPORT)-[A-Z0-9\-]+$", re.IGNORECASE)

    # 2. Header pattern heuristics
    HEADER_PATTERNS = {
        "EMAIL": re.compile(r"(?:^|[_\-])(?:e?mail|email_addr|contact_email|work_email|support_email)(?:[_\-]|$)", re.IGNORECASE),
        "PHONE_NUMBER": re.compile(r"(?:^|[_\-])(?:phone|mobile|cell|contact_no|contact_mobile|callback_number|tel(?:ephone)?)(?:[_\-]|$)", re.IGNORECASE),
        "NAME": re.compile(r"(?:^|[_\-])(?:full_name|first_name|last_name|employee_name|customer_name|requester_name|client_name|user_name|patient_name)(?:[_\-]|$)|^name$", re.IGNORECASE),
        "ADDRESS": re.compile(r"(?:^|[_\-])(?:address|residential_address|office_postal_address|dispatch_address|street_address|postal_address|shipping_address|billing_address)(?:[_\-]|$)", re.IGNORECASE),
        "GOVERNMENT_ID": re.compile(r"(?:^|[_\-])(?:synthetic_govt_id|national_id|national_id_synthetic|kyc_synthetic_ref|synthetic_tax_id|govt_id|aadhaar|pan_card|voter_id)(?:[_\-]|$)", re.IGNORECASE),
    }

    # Negative header patterns (e.g. company name, filename, category, status should not be flagged as personal NAME)
    NEGATIVE_NAME_HEADERS = re.compile(
        r"(?:company|org|organization|file|table|column|col|database|host|server|service|event|app|tag|project|schema|issue|category|status|type|dept|department|role|priority)_?",
        re.IGNORECASE
    )

    @classmethod
    def mask_value(cls, value: str, pii_class: str) -> str:
        """
        Masks sensitive-looking values to preserve privacy during review and logging.
        """
        if not value or not isinstance(value, str):
            return ""
        val = value.strip()
        if not val:
            return ""

        if pii_class == "EMAIL":
            if "@" in val:
                local_part, domain = val.split("@", 1)
                if len(local_part) <= 2:
                    masked_local = local_part[0] + "***"
                else:
                    masked_local = local_part[0] + "***" + local_part[-1]
                return f"{masked_local}@{domain}"
            return val[:2] + "***"

        elif pii_class == "PHONE_NUMBER":
            # Show prefix and last 2 digits
            digits = re.sub(r"\D", "", val)
            if len(digits) >= 10:
                return f"+91-*****-***{digits[-2:]}"
            return val[:3] + "****" + val[-2:] if len(val) > 5 else "****"

        elif pii_class == "NAME":
            parts = val.split()
            masked_parts = []
            for p in parts:
                if len(p) <= 2:
                    masked_parts.append(p[0] + "*")
                else:
                    masked_parts.append(p[0] + "*" * (len(p) - 2) + p[-1])
            return " ".join(masked_parts)

        elif pii_class == "ADDRESS":
            # Mask building/flat details and exact pin digits
            words = val.split(",")
            if len(words) > 2:
                masked_prefix = "Flat ***, [Street Masked]"
                city_part = words[-2].strip() if len(words) >= 2 else "City"
                return f"{masked_prefix}, {city_part}, [PIN Masked]"
            return val[:10] + "..." + " [Masked Address]"

        elif pii_class == "GOVERNMENT_ID":
            if "-" in val:
                parts = val.split("-")
                masked = "-".join([parts[0], parts[1] if len(parts) > 2 else "****"] + ["****"] * (len(parts) - 3) + [parts[-1]])
                return masked
            return val[:4] + "****" + val[-2:] if len(val) > 6 else "SYN-****"

        return val[:2] + "****"

    @classmethod
    def match_email(cls, val: str) -> bool:
        return bool(cls.EMAIL_REGEX.match(val.strip()))

    @classmethod
    def match_phone(cls, val: str) -> bool:
        v = val.strip()
        # Direct regex match
        if cls.PHONE_REGEX.match(v):
            return True
        # Strip spaces and hyphens and check 10-12 digits starting with valid Indian mobile/std prefixes
        clean = re.sub(r"[\s\-\(\)]", "", v)
        if clean.startswith("+91") and len(clean) == 13 and clean[3] in "6789":
            return True
        if clean.startswith("0") and len(clean) == 11 and clean[1] in "6789":
            return True
        if len(clean) == 10 and clean[0] in "6789":
            return True
        return False

    @classmethod
    def match_address(cls, val: str) -> bool:
        v = val.lower().strip()
        if len(v) < 12:
            return False
        # Count keyword occurrences
        keyword_hits = sum(1 for kw in cls.ADDRESS_KEYWORDS if kw in v)
        has_pin = bool(cls.INDIAN_PIN_REGEX.search(v))
        has_delimiters = "," in v or "-" in v
        return (keyword_hits >= 2 and has_delimiters) or (keyword_hits >= 1 and has_pin)

    @classmethod
    def match_govt_id(cls, val: str) -> bool:
        v = val.strip()
        if cls.SYN_AADHAAR_REGEX.match(v):
            return True
        if cls.SYN_PAN_REGEX.match(v):
            return True
        if cls.SYN_VOTER_REGEX.match(v):
            return True
        if cls.SYN_GENERIC_GOVT_REGEX.match(v):
            return True
        # Synthetic marker check
        if (v.startswith("SYN-") or v.startswith("SYNPA") or v.startswith("SYNVOT")) and len(v) >= 8:
            return True
        return False

    @classmethod
    def match_name(cls, val: str) -> bool:
        v = val.strip()
        if len(v) < 3 or len(v) > 50:
            return False
        # Names must not have digits, email symbols, or code tokens
        if re.search(r"[\d@#\$%^&*()_+=\[\]{};:\"\\|<>/]", v):
            return False
        parts = v.split()
        if len(parts) < 2 or len(parts) > 4:
            return False
        # Each part must be alphabetic and capitalized (or initials e.g. 'A.')
        for p in parts:
            clean_p = p.rstrip(".")
            if not clean_p.isalpha():
                return False
            if not p[0].isupper():
                return False
        return True

    def evaluate_column(
        self,
        column_name: str,
        sample_values: List[Any],
        source_name: str = "",
        table_name: str = ""
    ) -> DetectionResult:
        """
        Evaluates a single column using header heuristics and value pattern match rates.
        Combines signals into an explainable heuristic confidence score [0.0, 1.0].
        """
        # Convert and filter non-null string samples
        str_samples = []
        for s in sample_values:
            if s is not None and not (isinstance(s, float) and str(s) == "nan"):
                val_str = str(s).strip()
                if val_str and val_str.lower() != "null" and val_str.lower() != "none":
                    str_samples.append(val_str)

        sample_count = len(sample_values)
        non_null_count = len(str_samples)

        # Candidate evaluations across the 5 classes
        class_scores: Dict[str, Tuple[float, int, float, str, List[str]]] = {}

        for pii_class in ["EMAIL", "PHONE_NUMBER", "ADDRESS", "GOVERNMENT_ID", "NAME"]:
            header_regex = self.HEADER_PATTERNS[pii_class]
            header_hit = bool(header_regex.search(column_name))

            # Special check for negative name headers
            if pii_class == "NAME" and self.NEGATIVE_NAME_HEADERS.search(column_name):
                # Explicitly excluded non-personal entity names (company_name, file_name, etc.)
                class_scores[pii_class] = (0.0, 0, 0.0, f"Column '{column_name}' matched non-personal name exclusion pattern", [])
                continue

            # Test value matching
            matching_count = 0
            matching_samples = []

            for val in str_samples:
                matched = False
                if pii_class == "EMAIL":
                    matched = self.match_email(val)
                elif pii_class == "PHONE_NUMBER":
                    matched = self.match_phone(val)
                elif pii_class == "ADDRESS":
                    matched = self.match_address(val)
                elif pii_class == "GOVERNMENT_ID":
                    matched = self.match_govt_id(val)
                elif pii_class == "NAME":
                    matched = self.match_name(val)

                if matched:
                    matching_count += 1
                    if len(matching_samples) < 5:
                        matching_samples.append(val)

            match_rate = (matching_count / non_null_count) if non_null_count > 0 else 0.0

            # Calculate heuristic confidence score
            # Structure:
            # - Header score: up to 0.40
            # - Value match rate: up to 0.50
            # - Sample diversity / consistency bonus: up to 0.10
            header_weight = 0.40 if header_hit else 0.0
            value_weight = match_rate * 0.50
            diversity_bonus = 0.0

            if non_null_count >= 5 and match_rate > 0.5:
                # High uniqueness bonus for PII (names, emails, phones shouldn't be a single constant)
                uniqueness = len(set(str_samples)) / non_null_count
                if pii_class == "NAME" and not header_hit and uniqueness < 0.35:
                    # Low uniqueness without name header indicates categorical enum (e.g. issue_category, dept)
                    value_weight = value_weight * 0.4
                    diversity_bonus = -0.10
                elif uniqueness > 0.5:
                    diversity_bonus = 0.10
                elif uniqueness > 0.2:
                    diversity_bonus = 0.05

            score = header_weight + value_weight + diversity_bonus
            score = min(max(score, 0.0), 1.0)

            # Build explainable evidence text
            evidence_parts = []
            if header_hit:
                evidence_parts.append(f"Header pattern match on '{column_name}' (+{header_weight:.2f})")
            else:
                evidence_parts.append("No definitive header match")

            if non_null_count > 0:
                evidence_parts.append(f"{matching_count}/{non_null_count} sampled values ({match_rate*100:.1f}%) matched {pii_class} syntax (+{value_weight:.2f})")
            else:
                evidence_parts.append("Column has 0 non-null values to inspect")

            if diversity_bonus > 0:
                evidence_parts.append(f"High sample diversity (+{diversity_bonus:.2f})")

            evidence_str = "; ".join(evidence_parts)
            class_scores[pii_class] = (score, matching_count, match_rate, evidence_str, matching_samples)

        # Find best candidate class
        best_class = None
        best_score = 0.0
        best_meta = (0.0, 0, 0.0, "", [])

        for pii_class, meta in class_scores.items():
            score = meta[0]
            if score > best_score:
                best_score = score
                best_class = pii_class
                best_meta = meta

        # Decision Threshold:
        # A field is flagged as personal data if best_score >= 0.45 AND (either header matched OR match_rate >= 0.40)
        # Otherwise, NOT_PERSONAL
        is_personal = False
        final_class = None
        is_ambiguous = False
        notes = ""

        if best_class and best_score >= 0.45:
            # Check if ambiguous (e.g. match rate is low or conflicting headers)
            if best_meta[2] < 0.40 and not self.HEADER_PATTERNS[best_class].search(column_name):
                is_ambiguous = True
                notes = "Ambiguous candidate: partial pattern match with weak header evidence."
            elif 0.35 <= best_meta[2] <= 0.65 and not self.HEADER_PATTERNS[best_class].search(column_name):
                # Mixed column like contact_pref_token
                is_ambiguous = True
                notes = "Mixed data pattern observed across sample rows."
                # If ambiguous and no header match, we don't automatically flag as positive PII
                is_personal = False
                final_class = None
            else:
                is_personal = True
                final_class = best_class
                notes = f"High-confidence discovery for {best_class}."
        else:
            notes = "Insufficient evidence to classify as personal data."

        # Generate masked samples
        masked_samples = [
            self.mask_value(v, final_class or best_class or "UNKNOWN")
            for v in best_meta[4][:3]
        ]

        # Explicit reminder on heuristic score nature
        evidence_disclaimer = (
            f"{best_meta[3]}. [Note: Confidence score ({best_score:.2f}) is a heuristic "
            f"evidence metric based on rule match ratios; not a calibrated Bayesian probability.]"
        )

        return DetectionResult(
            source_name=source_name,
            table_name=table_name,
            column_name=column_name,
            detected_class=final_class,
            is_personal=is_personal,
            confidence_score=best_score if is_personal else (best_score if is_ambiguous else 0.0),
            header_matched=column_name if self.HEADER_PATTERNS.get(final_class or "", re.compile("$^")).search(column_name) else None,
            sample_count=sample_count,
            non_null_count=non_null_count,
            matching_sample_count=best_meta[1],
            sample_match_rate=best_meta[2],
            masked_samples=masked_samples,
            evidence_details=evidence_disclaimer,
            is_ambiguous=is_ambiguous,
            notes=notes
        )
