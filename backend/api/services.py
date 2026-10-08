from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from database import get_db
from schemas.service import (
    GovernmentServiceResponse,
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceCategoryResponse,
)
from schemas.common import MessageResponse
from auth.dependencies import get_current_user, get_current_admin_user
from models.users import User
import crud.crud_service as crud_service
from services.service_catalog import service_catalog_service

router = APIRouter(prefix="/services", tags=["Government Services Catalog"])


@router.get(
    "",
    response_model=List[GovernmentServiceResponse],
    status_code=status.HTTP_200_OK,
    summary="List all government services"
)
def list_services(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Retrieves list of active government services in the platform catalog.
    """
    return crud_service.get_all_services(db, skip=skip, limit=limit)


@router.get(
    "/categories",
    response_model=List[ServiceCategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="Get service categories and counts"
)
def get_categories(
    db: Session = Depends(get_db)
):
    """
    Returns categories of government services with scheme counts and department mappings.
    """
    return service_catalog_service.get_categories_with_counts(db)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Search services via hybrid keyword + vector search"
)
def search_services_endpoint(
    q: str = Query(..., min_length=1, description="Search query string"),
    category: Optional[str] = Query(None),
    department: Optional[str] = Query(None),
    district: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Hybrid Search API.
    Combines SQL keyword search with ChromaDB vector semantic search for ranked results.
    """
    results = service_catalog_service.hybrid_search_services(
        db=db,
        query=q,
        category=category,
        department=department,
        district=district,
        limit=limit
    )

    formatted = []
    for item in results:
        s = item["service"]
        formatted.append({
            "service_id": s.id,
            "title": s.title,
            "code": s.code,
            "category": s.category,
            "department": s.department,
            "description": s.description,
            "relevance_score": round(item["score"], 2),
            "match_type": item["match_type"],
            "processing_days": s.processing_days,
            "fee": s.fee_amount,
            "available_online": s.available_online
        })
    return formatted


@router.get(
    "/{service_id}",
    response_model=GovernmentServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get service details by ID"
)
def get_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieves full details of a specific government service scheme by ID.
    """
    service = crud_service.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Government service with ID {service_id} not found."
        )
    return service


# --- ADMIN CRUD ENDPOINTS (Protected via RBAC) ---

@router.post(
    "",
    response_model=GovernmentServiceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new government service (Admin Only)"
)
def create_new_service(
    service_in: ServiceCreateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Admin Endpoint: Creates a new government service entry in the catalog.
    Protected using Role-Based Access Control (Admin role required).
    """
    existing = crud_service.get_service_by_code(db, service_in.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Service with code '{service_in.code}' already exists."
        )
    return crud_service.create_service(db, service_in)


@router.put(
    "/{service_id}",
    response_model=GovernmentServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing government service (Admin Only)"
)
def update_existing_service(
    service_id: int,
    service_in: ServiceUpdateRequest,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    Admin Endpoint: Updates details of an existing government service.
    Protected using Role-Based Access Control (Admin role required).
    """
    service = crud_service.get_service_by_id(db, service_id)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Government service with ID {service_id} not found."
        )
    return crud_service.update_service(db, service, service_in)


@router.patch(
    "/{service_id}/status",
    response_model=GovernmentServiceResponse,
    status_code=status.HTTP_200_OK,
    summary="Soft update service status active/inactive (Admin Only)"
)
def update_service_status_endpoint(
    service_id: int,
    service_status: str = Body(..., embed=True, description="New service status e.g. 'active' or 'inactive'"),
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_admin_user)
):
    """
    PATCH /api/v1/services/{service_id}/status endpoint (Refinement #1).
    Soft updates government service status ('active', 'inactive', 'maintenance') without hard deleting database records.
    Protected using Role-Based Access Control (Admin role required).
    """
    service = crud_service.update_service_status(db, service_id, service_status)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Government service with ID {service_id} not found."
        )
    return service
