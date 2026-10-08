import pytest
from document_intelligence.ocr_engine import ocr_engine
from document_intelligence.field_extractors import mask_aadhaar, mask_pan, mask_bank_account


def test_ocr_failure_handling():
    """
    Test OCR failsafe handling when document is unreadable or missing.
    Must return 'ocr_failed' status without fabricating text.
    """
    res = ocr_engine.process_document(file_path="non_existent_file.png")
    assert res.status == "ocr_failed"
    assert "not found" in res.error_message.lower()


def test_sensitive_identifier_masking():
    """
    Test PII masking for Aadhaar, PAN, and Bank Account numbers.
    """
    masked_aadhaar = mask_aadhaar("1234 5678 9012")
    assert masked_aadhaar == "XXXX-XXXX-9012"
    assert "1234" not in masked_aadhaar

    masked_pan = mask_pan("ABCDE1234F")
    assert masked_pan == "XXXXX1234F"
    assert "ABCDE" not in masked_pan

    masked_bank = mask_bank_account("987654321012")
    assert masked_bank == "XXXX-XXXX-1012"
    assert "9876" not in masked_bank
