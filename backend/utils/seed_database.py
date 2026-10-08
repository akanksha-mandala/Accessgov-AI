import os
import json
import logging
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import Base, GovernmentService, ServiceRequirement

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("accessgov.utils.seed_database")


def seed_database(dataset_file_path: str = None):
    """
    Utility script (Refinement #2): Seeds JSON dataset records into PostgreSQL database tables.
    Fully idempotent: Updates existing records if matching code is found, preventing duplicate records across multiple runs.
    """
    if dataset_file_path is None:
        dataset_file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "datasets",
            "government_services.json"
        )

    if not os.path.exists(dataset_file_path):
        logger.error(f"Dataset JSON file not found at: {dataset_file_path}")
        return False

    with open(dataset_file_path, "r", encoding="utf-8") as f:
        services_data = json.load(f)

    db: Session = SessionLocal()
    try:
        updated_count = 0
        inserted_count = 0
        for item in services_data:
            code = item.get("code")
            service = db.query(GovernmentService).filter(GovernmentService.code == code).first()
            
            if service:
                # Idempotent Update
                service.title = item.get("title", item.get("service_name"))
                service.category = item.get("category", "General")
                service.service_category = item.get("service_category", item.get("category", "General"))
                service.department = item.get("department", "Revenue Department")
                service.department_name = item.get("department_name", item.get("department"))
                service.description = item.get("description", "")
                service.eligibility_criteria = item.get("eligibility_criteria", item.get("eligibility"))
                service.required_documents_summary = item.get("required_documents_summary")
                service.processing_time_days = item.get("processing_time_days", 7)
                service.processing_days = item.get("processing_days", 7)
                service.fee_amount = str(item.get("fee_amount", "Free"))
                service.validity_period = str(item.get("validity_period", "1 Year"))
                service.state = item.get("state", "Statewide")
                service.district_support = item.get("district_availability", ["All Districts"])
                updated_count += 1
            else:
                # Idempotent Insert
                service = GovernmentService(
                    title=item.get("title", item.get("service_name")),
                    code=code,
                    category=item.get("category", "General"),
                    service_category=item.get("service_category", item.get("category", "General")),
                    department=item.get("department", "Revenue Department"),
                    department_name=item.get("department_name", item.get("department")),
                    description=item.get("description", ""),
                    eligibility_criteria=item.get("eligibility_criteria", item.get("eligibility")),
                    required_documents_summary=item.get("required_documents_summary"),
                    processing_time_days=item.get("processing_time_days", 7),
                    processing_days=item.get("processing_days", 7),
                    fee_amount=str(item.get("fee_amount", "Free")),
                    validity_period=str(item.get("validity_period", "1 Year")),
                    is_active=True,
                    service_status="active",
                    available_online=True,
                    state=item.get("state", "Statewide"),
                    district_support=item.get("district_availability", ["All Districts"])
                )
                db.add(service)
                inserted_count += 1

            db.flush()  # Obtain service.id

            # Sync ServiceRequirement records idempotently
            req_docs = item.get("required_documents", [])
            for doc_name in req_docs:
                existing_req = db.query(ServiceRequirement).filter(
                    ServiceRequirement.service_id == service.id,
                    ServiceRequirement.document_name == doc_name
                ).first()
                if not existing_req:
                    req = ServiceRequirement(
                        service_id=service.id,
                        document_name=doc_name,
                        description=f"Required document: {doc_name}",
                        is_mandatory=True,
                        accepted_formats="pdf,jpg,png",
                        accepted_file_types="pdf,jpg,png",
                        max_file_size_mb=5,
                        verification_required=True
                    )
                    db.add(req)

        db.commit()
        logger.info(f"Idempotent database seeding completed. Inserted: {inserted_count}, Updated: {updated_count}.")
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Error during database seeding: {str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
