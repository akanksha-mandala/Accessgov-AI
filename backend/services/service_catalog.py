import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import crud.crud_service as crud_service

logger = logging.getLogger("accessgov.services.service_catalog")


class ServiceCatalogService:
    """
    Government Service Catalog.

    Service discovery uses the PostgreSQL service catalog directly.
    This keeps citizen-facing discovery fast and avoids loading the
    SentenceTransformer/ChromaDB RAG stack for simple service searches.
    """

    @staticmethod
    def hybrid_search_services(
        db: Session,
        query: str,
        category: Optional[str] = None,
        department: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fast service discovery using the PostgreSQL catalog.

        The previous implementation also performed semantic vector search,
        which could load SentenceTransformer and cause 20-40+ second delays.
        SQL keyword search is sufficient for the government service catalog
        and is the primary source of truth for service discovery.
        """

        try:
            sql_matches = crud_service.search_services(
                db=db,
                query=query,
                category=category,
                department=department,
                district=district,
                limit=limit * 2
            )

            results_map: Dict[int, Dict[str, Any]] = {}

            for s in sql_matches:
                description = s.description or ""

                results_map[s.id] = {
                    "service": s,
                    "score": 0.90,
                    "match_type": "keyword",
                    "snippet": (
                        description[:200] + "..."
                        if len(description) > 200
                        else description
                    )
                }

            # Apply district availability filtering.
            if district and district.strip():
                filtered = []

                for item in results_map.values():
                    dist_list = item["service"].district_support or ["All Districts"]

                    if (
                        "All Districts" in dist_list
                        or "All" in dist_list
                        or district in dist_list
                    ):
                        filtered.append(item)

                final_list = filtered
            else:
                final_list = list(results_map.values())

            final_list.sort(
                key=lambda x: x["score"],
                reverse=True
            )

            return final_list[:limit]

        except Exception as e:
            logger.error(
                "Service catalog search failed: %s",
                str(e),
                exc_info=True
            )
            return []

    @staticmethod
    def get_categories_with_counts(
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Lists available service categories along with scheme counts
        and department mappings.
        """

        services = crud_service.get_all_services(db, limit=500)
        category_map: Dict[str, Dict[str, Any]] = {}

        for s in services:
            cat = s.category or "General"

            if cat not in category_map:
                category_map[cat] = {
                    "category": cat,
                    "count": 0,
                    "departments": set()
                }

            category_map[cat]["count"] += 1

            if s.department:
                category_map[cat]["departments"].add(s.department)

        return [
            {
                "category": data["category"],
                "count": data["count"],
                "departments": list(data["departments"])
            }
            for data in category_map.values()
        ]


service_catalog_service = ServiceCatalogService()