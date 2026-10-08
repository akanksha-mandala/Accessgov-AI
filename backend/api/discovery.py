from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session

from database import get_db
from schemas.service import ServiceDiscoveryRequest
from schemas.requirement import RequiredDocument, SimpleExplanationResponse

import crud.crud_service as crud_service
import crud.crud_requirement as crud_requirement

from services.service_catalog import service_catalog_service
from services.simplifier import simplifier_service
from services.translation_service import translation_service


router = APIRouter(
    prefix="/services",
    tags=["Service Discovery & Plain Language"]
)


@router.post(
    "/discover",
    status_code=status.HTTP_200_OK,
    summary="Discover relevant government services for citizen intent"
)
def discover_services(
    request: ServiceDiscoveryRequest,
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/services/discover endpoint.

    Performs discovery matching citizen query, user category,
    and district against the service catalog.
    """
    query_str = (
        request.query
        or request.user_category
        or "general services"
    )

    results = service_catalog_service.hybrid_search_services(
        db=db,
        query=query_str,
        category=request.user_category,
        district=request.district,
        limit=5
    )

    discovered = []

    for item in results:
        s = item["service"]

        # Translate description if a non-English language is requested.
        description = s.description

        if request.language and request.language != "en":
            description = translation_service.translate_text(
                description,
                target_lang=request.language
            )

        discovered.append({
            "service_id": s.id,
            "title": s.title,
            "code": s.code,
            "category": s.category,
            "department": s.department,
            "description": description,
            "match_confidence": item["score"],
            "processing_days": s.processing_days,
            "fee": s.fee_amount
        })

    return {
        "query": query_str,
        "language": request.language,
        "district": request.district,
        "total_discovered": len(discovered),
        "services": discovered
    }


@router.post(
    "/requirements",
    response_model=List[RequiredDocument],
    status_code=status.HTTP_200_OK,
    summary="Get required documents for a service"
)
def get_service_requirements_endpoint(
    service_id: int = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    """
    POST /api/v1/services/requirements endpoint.

    Returns the list of required documents for applying
    for a government service.
    """
    service = crud_service.get_service_by_id(
        db,
        service_id
    )

    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service with ID {service_id} not found."
        )

    reqs = crud_requirement.get_service_requirements(
        db,
        service_id
    )

    if not reqs:
        # Generate default requirements if specific
        # database records are not yet populated.
        return [
            RequiredDocument(
                service_id=service_id,
                document_name="Aadhaar Card",
                description="Proof of Identity & Address",
                is_mandatory=True
            ),
            RequiredDocument(
                service_id=service_id,
                document_name="Ration Card / Smart Card",
                description="Proof of Family Composition",
                is_mandatory=True
            ),
            RequiredDocument(
                service_id=service_id,
                document_name="Passport Photograph",
                description="Recent colored passport photograph",
                is_mandatory=True
            )
        ]

    return reqs


@router.post(
    "/simple-explanation",
    response_model=SimpleExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Convert government terminology into citizen-friendly plain language"
)
def get_simple_explanation(
    term: str = Body(
        ...,
        embed=True,
        description="Government term e.g. 'Domicile Certificate'"
    ),
    language: str = Body(
        "en",
        embed=True,
        description="Language code: en, ta, te, hi, kn"
    )
):
    """
    POST /api/v1/services/simple-explanation endpoint.

    Translates complex administrative terms into simple
    citizen explanations with key points.
    """
    explanation = simplifier_service.simplify_term(
        term,
        language=language
    )

    return explanation


@router.post(
    "/translate",
    status_code=status.HTTP_200_OK,
    summary="Translate text into the selected citizen language"
)
def translate_text_endpoint(
    text: str = Body(
        ...,
        embed=True,
        description="Text to translate"
    ),
    target_language: str = Body(
        "en",
        embed=True,
        description="Target language code: en, ta, te, hi, kn"
    ),
    source_language: str = Body(
        "en",
        embed=True,
        description="Source language code: en, ta, te, hi, kn"
    ),
):
    """
    POST /api/v1/services/translate

    Translates arbitrary frontend/page text using the
    existing TranslationService.
    """
    translated = translation_service.translate_text(
        text=text,
        target_lang=target_language,
        source_lang=source_language,
    )

    return {
        "text": translated,
        "source_language": source_language,
        "target_language": target_language,
    }