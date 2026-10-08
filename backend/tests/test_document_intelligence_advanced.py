import os
import io
import tempfile
import pytest
from fastapi import UploadFile, HTTPException
from schemas.document import OCRResult, ValidationResult
from document_intelligence.document_classifier import document_classifier
from document_intelligence.field_extractors import (
    field_extractor_engine,
    mask_aadhaar,
    mask_pan,
    mask_bank_account
)
from document_intelligence.validators import document_validator
from document_intelligence.readiness_engine import document_readiness_engine
from document_intelligence.ocr_engine import ocr_engine
from utils.file_storage import file_storage_util


def test_file_storage_supported_formats():
    """
    Test validation of supported file formats (PDF, PNG, JPG, JPEG).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = file_storage_util.__class__(storage_path=tmp_dir, max_size_mb=10)
        
        # Valid PNG upload
        png_content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        upload = UploadFile(filename="test_doc.png", file=io.BytesIO(png_content), headers={"content-type": "image/png"})
        saved_path, unique_fn, file_size, mime = storage.validate_and_save_upload(upload)
        assert os.path.exists(saved_path)
        assert unique_fn.endswith(".png")
        assert file_size == len(png_content)


def test_unsupported_file_extension():
    """
    Test rejection of unsupported file extensions (e.g., .exe, .txt).
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = file_storage_util.__class__(storage_path=tmp_dir, max_size_mb=10)
        upload = UploadFile(filename="malicious_script.exe", file=io.BytesIO(b"echo hello"), headers={"content-type": "application/x-msdownload"})
        
        with pytest.raises(HTTPException) as exc_info:
            storage.validate_and_save_upload(upload)
        assert exc_info.value.status_code == 400
        assert "Unsupported file format" in exc_info.value.detail


def test_oversized_file_limit():
    """
    Test enforcement of 10MB size limit before processing.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = file_storage_util.__class__(storage_path=tmp_dir, max_size_mb=1)  # 1MB limit for testing
        large_content = b"0" * (2 * 1024 * 1024)  # 2MB
        upload = UploadFile(filename="large_document.pdf", file=io.BytesIO(large_content), headers={"content-type": "application/pdf"})
        
        with pytest.raises(HTTPException) as exc_info:
            storage.validate_and_save_upload(upload)
        assert exc_info.value.status_code == 400
        assert "exceeds maximum limit" in exc_info.value.detail


def test_empty_or_corrupted_file():
    """
    Test rejection of 0-byte empty files.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        storage = file_storage_util.__class__(storage_path=tmp_dir, max_size_mb=10)
        upload = UploadFile(filename="empty.jpg", file=io.BytesIO(b""), headers={"content-type": "image/jpeg"})
        
        with pytest.raises(HTTPException) as exc_info:
            storage.validate_and_save_upload(upload)
        assert exc_info.value.status_code == 400
        assert "Empty file uploaded" in exc_info.value.detail


def test_unknown_document_classification():
    """
    Test classification of unrecognized text yielding 'Unknown Document' with low confidence.
    """
    random_text = "The quick brown fox jumps over the lazy dog 12345 lorem ipsum."
    doc_type, confidence, indicators = document_classifier.classify_text(random_text)
    assert doc_type == "Unknown Document"
    assert confidence < 0.60


def test_aadhaar_extraction_and_masking():
    """
    Test Aadhaar extraction with strict PII masking (XXXX-XXXX-9012).
    """
    text = "GOVERNMENT OF INDIA Aadhaar Card Name: Rajesh Kumar DOB: 12/05/1988 Gender: Male 1234 5678 9012"
    fields = field_extractor_engine.extract_aadhaar_fields(text)
    assert fields["aadhaar_number"] == "XXXX-XXXX-9012"
    assert fields["dob"] == "12/05/1988"
    assert fields["gender"] == "Male"


def test_malformed_aadhaar_extraction():
    """
    Test malformed Aadhaar number handling (fewer than 12 digits).
    """
    text = "Aadhaar Card Name: Suresh DOB: 01/01/1990 Aadhaar: 1234 567"
    fields = field_extractor_engine.extract_aadhaar_fields(text)
    assert fields["aadhaar_number"] is None


def test_pan_extraction_and_masking():
    """
    Test PAN card extraction with strict PII masking (XXXXX1234F).
    """
    text = "INCOME TAX DEPARTMENT Permanent Account Number ABCDE1234F Name: Anita Sharma DOB: 25/11/1992"
    fields = field_extractor_engine.extract_pan_fields(text)
    assert fields["pan_number"] == "XXXXX1234F"
    assert fields["dob"] == "25/11/1992"


def test_malformed_pan_extraction():
    """
    Test malformed PAN number handling (invalid format).
    """
    text = "INCOME TAX DEPARTMENT PAN Number 12345ABCDE"
    fields = field_extractor_engine.extract_pan_fields(text)
    assert fields["pan_number"] is None


def test_bank_passbook_account_masking():
    """
    Test Bank account number masking (XXXX-XXXX-1012).
    """
    masked = mask_bank_account("987654321012")
    assert masked == "XXXX-XXXX-1012"
    assert "98765432" not in masked


def test_missing_mandatory_fields_validation():
    """
    Test validator marking status as 'incomplete' when mandatory fields are missing.
    """
    fields = {"name": "Rajesh Kumar", "aadhaar_number": None, "dob": "12/05/1988"}
    res = document_validator.validate_extracted_fields("Aadhaar Card", fields, ocr_confidence=0.90)
    assert res.is_valid is False
    assert res.validation_status == "incomplete"
    assert "aadhaar_number" in res.missing_fields


def test_low_ocr_confidence_warning():
    """
    Test validator appending warning when OCR confidence is below 0.70.
    """
    fields = {"pan_number": "XXXXX1234F"}
    res = document_validator.validate_extracted_fields("PAN Card", fields, ocr_confidence=0.55)
    assert any("Low OCR text extraction confidence" in w for w in res.warnings)


def test_readiness_score_boundaries():
    """
    Test readiness score boundaries (0.0 for unknown document, 100.0 for complete high-quality document).
    """
    # Boundary 0.0
    val_unknown = ValidationResult(is_valid=False, validation_status="incomplete", missing_fields=[], warnings=[], extracted_fields={})
    res_0 = document_readiness_engine.calculate_readiness("Unknown Document", {}, val_unknown, ocr_confidence=0.0)
    assert res_0.readiness_score == 0.0

    # Boundary 100.0
    fields_complete = {"pan_number": "XXXXX1234F", "dob": "01/01/1990"}
    val_valid = ValidationResult(is_valid=True, validation_status="valid", missing_fields=[], warnings=[], extracted_fields=fields_complete)
    res_100 = document_readiness_engine.calculate_readiness("PAN Card", fields_complete, val_valid, ocr_confidence=1.0)
    assert res_100.readiness_score == 100.0


def test_ocr_failure_handling():
    """
    Test OCR engine returning structured failure result without generating fake text.
    """
    result = ocr_engine.process_document(file_path="C:/non_existent_file.jpg", mime_type="image/jpeg")
    assert result.status == "ocr_failed"
    assert result.raw_text == ""
    assert "not found" in result.error_message.lower()
