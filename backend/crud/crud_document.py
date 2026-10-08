from typing import List, Optional

from sqlalchemy.orm import Session

from models.uploaded_documents import UploadedDocument, VerificationStatus


def create_document_record(
    db: Session,
    user_id: int,
    file_name: str,
    file_path: str,
    mime_type: str,
    file_size_bytes: int,
    document_type: str = "Unknown Document",
    application_id: Optional[int] = None,
    ocr_status: Optional[str] = None,
    ocr_confidence: Optional[float] = None,
    readability_score: Optional[float] = None,
    sharpness_score: Optional[float] = None,
    readiness_score: Optional[float] = None,
    quality_issues: Optional[list] = None,
    extracted_fields: Optional[dict] = None,
    validation_errors: Optional[list] = None,
) -> UploadedDocument:
    """
    Creates a new UploadedDocument record in the database
    and persists the document intelligence inspection results.
    """
    doc = UploadedDocument(
        user_id=user_id,
        application_id=application_id,
        document_type=document_type,
        file_name=file_name,
        file_path=file_path,
        mime_type=mime_type,
        file_size_bytes=file_size_bytes,
        verification_status=VerificationStatus.PENDING,

        # Persisted document intelligence results
        ocr_status=ocr_status,
        ocr_confidence=ocr_confidence,
        readability_score=readability_score,
        sharpness_score=sharpness_score,
        readiness_score=readiness_score,
        quality_issues=quality_issues or [],
        extracted_fields=extracted_fields or {},
        validation_errors=validation_errors or [],
    )

    db.add(doc)
    db.commit()
    db.refresh(doc)

    return doc


def get_document_by_id(db: Session, document_id: int) -> Optional[UploadedDocument]:
    """
    Retrieves an UploadedDocument record by primary key ID.
    """
    if db is None:
        return None

    return (
        db.query(UploadedDocument)
        .filter(UploadedDocument.id == document_id)
        .first()
    )


def list_user_documents(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 50
) -> List[UploadedDocument]:
    """
    Lists documents belonging to a citizen.

    Rejected documents are excluded from the personal vault.
    Pending documents remain visible because they may require review.
    """
    if db is None:
        return []

    return (
        db.query(UploadedDocument)
        .filter(
            UploadedDocument.user_id == user_id,
            UploadedDocument.verification_status != VerificationStatus.REJECTED
        )
        .order_by(
            UploadedDocument.uploaded_at.desc()
        )
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_document_status(
    db: Session,
    document_id: int,
    status: VerificationStatus,
    rejection_reason: Optional[str] = None
) -> Optional[UploadedDocument]:
    """
    Updates verification status ('pending', 'verified', 'rejected') of a document.
    """
    doc = get_document_by_id(db, document_id)

    if doc:
        doc.verification_status = status

        if rejection_reason:
            doc.rejection_reason = rejection_reason

        db.add(doc)
        db.commit()
        db.refresh(doc)

    return doc


def update_document_type(
    db: Session,
    document_id: int,
    document_type: str
) -> Optional[UploadedDocument]:
    """
    Updates classified document type (e.g. 'Income Certificate', 'Aadhaar Card').
    """
    doc = get_document_by_id(db, document_id)

    if doc:
        doc.document_type = document_type
        db.add(doc)
        db.commit()
        db.refresh(doc)

    return doc


def soft_delete_document(
    db: Session,
    document_id: int
) -> Optional[UploadedDocument]:
    """
    Soft deletes document record by setting status to REJECTED
    and adding deletion note.
    """
    return update_document_status(
        db,
        document_id=document_id,
        status=VerificationStatus.REJECTED,
        rejection_reason="User deleted / revoked document access."
    )