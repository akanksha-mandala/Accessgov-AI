from typing import List, Optional
from sqlalchemy.orm import Session
from models.service_requirements import ServiceRequirement


def get_service_requirements(db: Session, service_id: int) -> List[ServiceRequirement]:
    """
    Retrieves all document requirements for a specific government service.
    """
    return db.query(ServiceRequirement).filter(ServiceRequirement.service_id == service_id).all()


def get_requirement_documents(db: Session, service_id: int) -> List[str]:
    """
    Returns list of document names required for a service.
    """
    reqs = get_service_requirements(db, service_id)
    return [r.document_name for r in reqs]


def create_service_requirement(
    db: Session,
    service_id: int,
    document_name: str,
    description: Optional[str] = None,
    is_mandatory: bool = True,
    accepted_file_types: str = "pdf,jpg,png",
    max_file_size_mb: int = 5
) -> ServiceRequirement:
    """
    Adds a document requirement entry for a government service.
    """
    req = ServiceRequirement(
        service_id=service_id,
        document_name=document_name,
        description=description,
        is_mandatory=is_mandatory,
        accepted_formats=accepted_file_types,
        accepted_file_types=accepted_file_types,
        max_file_size_mb=max_file_size_mb,
        verification_required=True
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req
