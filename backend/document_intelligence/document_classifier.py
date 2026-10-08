import re
import logging
from typing import Tuple, List, Dict, Any
from rapidfuzz import fuzz
from config import settings

logger = logging.getLogger("accessgov.document_intelligence.document_classifier")

# Document Classification Rules & Indicator Dictionary
DOCUMENT_PATTERNS: Dict[str, Dict[str, Any]] = {
    "Aadhaar Card": {
        "keywords": ["unique identification authority", "uidai", "aadhaar", "adhar", "government of india", "mera aadhaar"],
        "regex": [r"\b\d{4}\s?\d{4}\s?\d{4}\b", r"male|female"],
        "weight": 1.0
    },
    "PAN Card": {
        "keywords": ["income tax department", "permanent account number", "govt of india", "tax department"],
        "regex": [r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"],
        "weight": 1.0
    },
    "Income Certificate": {
        "keywords": ["income certificate", "annual income", "tahsildar", "revenue department", "certified that annual income"],
        "regex": [r"annual\s+income", r"rs\.?\s?\d+"],
        "weight": 0.90
    },
    "Community / Caste Certificate": {
        "keywords": ["caste certificate", "community certificate", "scheduled caste", "scheduled tribe", "backward class", "obc", "bc", "sc/st"],
        "regex": [r"belongs\s+to", r"community"],
        "weight": 0.90
    },
    "Domicile Certificate": {
        "keywords": ["domicile certificate", "residence certificate", "nativity certificate", "permanent resident"],
        "regex": [r"resident\s+of", r"domicile"],
        "weight": 0.90
    },
    "Birth Certificate": {
        "keywords": ["birth certificate", "date of birth", "place of birth", "department of public health", "vital statistics"],
        "regex": [r"born\s+on", r"birth"],
        "weight": 0.90
    },
    "Disability Certificate": {
        "keywords": ["disability certificate", "udid", "unique disability id", "percentage of disability", "differently abled", "benchmark disability"],
        "regex": [r"\b\d{1,2}%\s+disability\b", r"udid"],
        "weight": 0.95
    },
    "Pension Certificate": {
        "keywords": ["pension certificate", "pension payment order", "ppo", "old age pension", "widow pension", "social welfare pension"],
        "regex": [r"pension", r"ppo"],
        "weight": 0.90
    },
    "Bank Passbook": {
        "keywords": ["bank passbook", "account number", "ifs code", "ifsc", "branch name", "savings bank", "bank of"],
        "regex": [r"\b[A-Z]{4}0[A-Z0-9]{6}\b", r"account\s+no"],
        "weight": 0.90
    }
}


class DocumentClassifier:
    """
    Deterministic & Explainable Document Classifier (Refinement #4).
    Combines keyword density, regex matching, and RapidFuzz fuzzy string similarity.
    Classifies as 'Unknown Document' if confidence is below OCR_CONFIDENCE_THRESHOLD (0.60).
    """

    def __init__(self, threshold: float = None):
        self.threshold = threshold or settings.OCR_CONFIDENCE_THRESHOLD

    def classify_text(self, text: str) -> Tuple[str, float, List[str]]:
        """
        Classifies extracted text into a supported document type.
        Returns Tuple[document_type, confidence_score, matched_indicators].
        """
        if not text or len(text.strip()) < 10:
            return "Unknown Document", 0.0, ["Insufficient text extracted for classification"]

        text_lower = text.lower()
        scores: Dict[str, float] = {}
        indicators: Dict[str, List[str]] = {}

        for doc_type, rules in DOCUMENT_PATTERNS.items():
            match_score = 0.0
            matched_list = []

            # 1. Keyword Matching
            for kw in rules["keywords"]:
                if kw in text_lower:
                    match_score += 0.35
                    matched_list.append(f"Keyword: '{kw}'")
                else:
                    # Fuzzy String Matching via RapidFuzz
                    fuzz_ratio = fuzz.partial_ratio(kw, text_lower)
                    if fuzz_ratio > 85:
                        match_score += 0.20
                        matched_list.append(f"Fuzzy Match: '{kw}' ({fuzz_ratio}%)")

            # 2. Regex Pattern Matching
            for pattern in rules["regex"]:
                if re.search(pattern, text, re.IGNORECASE):
                    match_score += 0.45
                    matched_list.append(f"Regex Pattern: {pattern}")

            total_score = min(1.0, match_score * rules["weight"])
            scores[doc_type] = total_score
            indicators[doc_type] = matched_list

        best_doc_type = max(scores, key=scores.get)
        best_confidence = round(scores[best_doc_type], 2)
        best_indicators = indicators[best_doc_type]

        if best_confidence < self.threshold:
            logger.info(f"Classification confidence {best_confidence} below threshold {self.threshold}. Classifying as 'Unknown Document'.")
            return "Unknown Document", best_confidence, ["Classification confidence below threshold (0.60)"]

        logger.info(f"Classified document as '{best_doc_type}' with confidence {best_confidence}")
        return best_doc_type, best_confidence, best_indicators


document_classifier = DocumentClassifier()
