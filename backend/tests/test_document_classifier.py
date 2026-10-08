import pytest
from document_intelligence.document_classifier import document_classifier


def test_document_classifier_aadhaar():
    """
    Test classification of Aadhaar Card text.
    """
    sample_text = "Government of India UIDAI Unique Identification Authority 1234 5678 9012 Male"
    doc_type, conf, indicators = document_classifier.classify_text(sample_text)
    assert doc_type == "Aadhaar Card"
    assert conf >= 0.60
    assert len(indicators) > 0


def test_document_classifier_pan():
    """
    Test classification of PAN Card text.
    """
    sample_text = "INCOME TAX DEPARTMENT GOVT OF INDIA Permanent Account Number ABCDE1234F"
    doc_type, conf, indicators = document_classifier.classify_text(sample_text)
    assert doc_type == "PAN Card"
    assert conf >= 0.60


def test_document_classifier_unknown_document():
    """
    Test low-confidence classification falling back to 'Unknown Document'.
    """
    sample_text = "Unclear blurry text without keywords"
    doc_type, conf, indicators = document_classifier.classify_text(sample_text)
    assert doc_type == "Unknown Document"
    assert conf < 0.60
