from typing import List, Optional, Union, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models.government_services import GovernmentService
from schemas.service import ServiceCreateRequest, ServiceUpdateRequest


def get_all_services(db: Session, skip: int = 0, limit: int = 100, active_only: bool = True) -> List[GovernmentService]:
    """
    Retrieves list of government services with optional active status filter.
    """
    if db is None:
        return []
    query = db.query(GovernmentService)
    if active_only:
        query = query.filter(GovernmentService.service_status == "active", GovernmentService.is_active == True)
    return query.offset(skip).limit(limit).all()


def get_service_by_id(db: Session, service_id: int) -> Optional[GovernmentService]:
    """
    Retrieves a government service by primary key ID.
    """
    if db is None:
        return None
    return db.query(GovernmentService).filter(GovernmentService.id == service_id).first()


def get_service_by_code(db: Session, code: str) -> Optional[GovernmentService]:
    """
    Retrieves a government service by unique code (e.g. "GOV-INC-001").
    """
    if db is None:
        return None
    return db.query(GovernmentService).filter(GovernmentService.code == code.strip()).first()


def search_services(
    db: Session,
    query: str,
    category: Optional[str] = None,
    department: Optional[str] = None,
    district: Optional[str] = None,
    limit: int = 10
) -> List[GovernmentService]:
    """
    Performs keyword & attribute filtering search across title, description, category, and department.
    """
    q = db.query(GovernmentService).filter(
        GovernmentService.service_status == "active",
        GovernmentService.is_active == True
    )

    if query and query.strip():
        search_pattern = f"%{query.strip()}%"
        q = q.filter(
            or_(
                GovernmentService.title.ilike(search_pattern),
                GovernmentService.description.ilike(search_pattern),
                GovernmentService.category.ilike(search_pattern),
                GovernmentService.department.ilike(search_pattern),
                GovernmentService.eligibility_criteria.ilike(search_pattern)
            )
        )

    if category:
        q = q.filter(or_(GovernmentService.category.ilike(category), GovernmentService.service_category.ilike(category)))

    if department:
        q = q.filter(or_(GovernmentService.department.ilike(department), GovernmentService.department_name.ilike(department)))

    return q.limit(limit).all()


def get_services_by_category(db: Session, category: str) -> List[GovernmentService]:
    """
    Retrieves services under a given category string.
    """
    return db.query(GovernmentService).filter(
        GovernmentService.service_status == "active",
        or_(GovernmentService.category.ilike(category), GovernmentService.service_category.ilike(category))
    ).all()


def get_services_by_department(db: Session, department: str) -> List[GovernmentService]:
    """
    Retrieves services offered by a specific department.
    """
    return db.query(GovernmentService).filter(
        GovernmentService.service_status == "active",
        or_(GovernmentService.department.ilike(department), GovernmentService.department_name.ilike(department))
    ).all()


def create_service(db: Session, service_in: ServiceCreateRequest) -> GovernmentService:
    """
    Creates a new government service catalog entry (Admin function).
    """
    db_service = GovernmentService(
        title=service_in.title,
        code=service_in.code,
        category=service_in.category,
        service_category=service_in.category,
        department=service_in.department,
        department_name=service_in.department,
        description=service_in.description,
        eligibility_criteria=service_in.eligibility_criteria,
        required_documents_summary=service_in.required_documents_summary,
        processing_time_days=service_in.processing_days,
        processing_days=service_in.processing_days,
        fee_amount=service_in.fee_amount,
        validity_period=service_in.validity_period,
        state=service_in.state,
        district_support=service_in.district_support,
        is_active=True,
        service_status="active",
        available_online=True
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def update_service(db: Session, db_service: GovernmentService, service_in: ServiceUpdateRequest) -> GovernmentService:
    """
    Updates existing government service fields (Admin function).
    """
    update_data = service_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(db_service, field) and value is not None:
            setattr(db_service, field, value)

    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service


def update_service_status(db: Session, service_id: int, new_status: str) -> Optional[GovernmentService]:
    """
    Updates government service status ('active', 'inactive', 'maintenance') (Refinement #1).
    """
    service = get_service_by_id(db, service_id)
    if service:
        clean_status = new_status.lower().strip()
        service.service_status = clean_status
        service.is_active = (clean_status == "active")
        db.add(service)
        db.commit()
        db.refresh(service)
    return service


def disable_service(db: Session, service_id: int) -> Optional[GovernmentService]:
    """
    Soft status update marking a service as 'inactive' rather than permanent database deletion.
    """
    return update_service_status(db, service_id, "inactive")


def list_departments(db: Session) -> List[str]:
    """
    Returns distinct list of government departments operating schemes.
    """
    results = db.query(GovernmentService.department).distinct().all()
    return [r[0] for r in results if r[0]]
