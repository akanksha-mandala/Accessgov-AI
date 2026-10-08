from datetime import datetime, timezone
from sqlalchemy import text
from database import SessionLocal


def seed():
    db = SessionLocal()

    try:
        # ---------------------------------------------------------
        # 1. Scholarship demo service
        # ---------------------------------------------------------
        scholarship = db.execute(
            text("""
                INSERT INTO government_services (
                    title,
                    code,
                    category,
                    service_category,
                    department,
                    department_name,
                    description,
                    eligibility_criteria,
                    required_documents_summary,
                    processing_time_days,
                    processing_days,
                    fee_amount,
                    validity_period,
                    is_active,
                    service_status,
                    available_online,
                    state,
                    district_support,
                    created_at,
                    updated_at
                )
                VALUES (
                    :title,
                    :code,
                    :category,
                    :service_category,
                    :department,
                    :department_name,
                    :description,
                    :eligibility_criteria,
                    :required_documents_summary,
                    :processing_time_days,
                    :processing_days,
                    :fee_amount,
                    :validity_period,
                    :is_active,
                    :service_status,
                    :available_online,
                    :state,
                    CAST(:district_support AS json),
                    :created_at,
                    :updated_at
                )
                RETURNING id
            """),
            {
                "title": "Scholarship",
                "code": "SCHOLARSHIP",
                "category": "Education",
                "service_category": "Scholarship",
                "department": "Education Department",
                "department_name": "Education Department",
                "description": (
                    "Demo scholarship service for students. "
                    "The service helps eligible students understand "
                    "the scholarship application process and required documents."
                ),
                "eligibility_criteria": (
                    "Eligibility depends on the specific scholarship scheme. "
                    "For this demo, students should verify their student status "
                    "and scheme-specific eligibility requirements before applying."
                ),
                "required_documents_summary": (
                    "Aadhaar Card, Student ID or Bonafide Certificate, "
                    "Income Certificate, Bank Account Details, "
                    "Passport Photograph"
                ),
                "processing_time_days": 15,
                "processing_days": 15,
                "fee_amount": "No fee for this demo service",
                "validity_period": "As specified by the applicable scholarship scheme",
                "is_active": True,
                "service_status": "active",
                "available_online": True,
                "state": "Tamil Nadu",
                "district_support": '["All Districts"]',
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ).scalar_one()

        # ---------------------------------------------------------
        # 2. Income Certificate demo service
        # ---------------------------------------------------------
        income = db.execute(
            text("""
                INSERT INTO government_services (
                    title,
                    code,
                    category,
                    service_category,
                    department,
                    department_name,
                    description,
                    eligibility_criteria,
                    required_documents_summary,
                    processing_time_days,
                    processing_days,
                    fee_amount,
                    validity_period,
                    is_active,
                    service_status,
                    available_online,
                    state,
                    district_support,
                    created_at,
                    updated_at
                )
                VALUES (
                    :title,
                    :code,
                    :category,
                    :service_category,
                    :department,
                    :department_name,
                    :description,
                    :eligibility_criteria,
                    :required_documents_summary,
                    :processing_time_days,
                    :processing_days,
                    :fee_amount,
                    :validity_period,
                    :is_active,
                    :service_status,
                    :available_online,
                    :state,
                    CAST(:district_support AS json),
                    :created_at,
                    :updated_at
                )
                RETURNING id
            """),
            {
                "title": "Income Certificate",
                "code": "INCOME_CERTIFICATE",
                "category": "Certificates",
                "service_category": "Income Certificate",
                "department": "Revenue Department",
                "department_name": "Revenue Department",
                "description": (
                    "Demo income certificate service for citizens who need "
                    "to understand the application process and supporting documents."
                ),
                "eligibility_criteria": (
                    "The applicant should provide information and supporting "
                    "documents required to establish family or individual income "
                    "according to the applicable authority's requirements."
                ),
                "required_documents_summary": (
                    "Aadhaar Card, Address Proof, "
                    "Income-related Supporting Document, "
                    "Passport Photograph"
                ),
                "processing_time_days": 7,
                "processing_days": 7,
                "fee_amount": "No fee for this demo service",
                "validity_period": "As specified by the issuing authority",
                "is_active": True,
                "service_status": "active",
                "available_online": True,
                "state": "Tamil Nadu",
                "district_support": '["All Districts"]',
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            },
        ).scalar_one()

        # ---------------------------------------------------------
        # 3. Requirements for Scholarship
        # ---------------------------------------------------------
        scholarship_requirements = [
            (
                scholarship,
                "Aadhaar Card",
                "Identity verification document.",
            ),
            (
                scholarship,
                "Student ID or Bonafide Certificate",
                "Proof of student status.",
            ),
            (
                scholarship,
                "Income Certificate",
                "Income-related supporting document where required by the scheme.",
            ),
            (
                scholarship,
                "Bank Account Details",
                "Bank account information for scholarship-related processing.",
            ),
            (
                scholarship,
                "Passport Photograph",
                "Recent applicant photograph.",
            ),
        ]

        # ---------------------------------------------------------
        # 4. Requirements for Income Certificate
        # ---------------------------------------------------------
        income_requirements = [
            (
                income,
                "Aadhaar Card",
                "Identity verification document.",
            ),
            (
                income,
                "Address Proof",
                "Proof of residential address.",
            ),
            (
                income,
                "Income-related Supporting Document",
                "Supporting evidence used for income verification.",
            ),
            (
                income,
                "Passport Photograph",
                "Recent applicant photograph.",
            ),
        ]

        now = datetime.now(timezone.utc)

        for service_id, document_name, description in (
            scholarship_requirements + income_requirements
        ):
            db.execute(
                text("""
                    INSERT INTO service_requirements (
                        service_id,
                        document_name,
                        description,
                        is_mandatory,
                        accepted_formats,
                        accepted_file_types,
                        max_file_size_mb,
                        verification_required,
                        created_at
                    )
                    VALUES (
                        :service_id,
                        :document_name,
                        :description,
                        :is_mandatory,
                        :accepted_formats,
                        :accepted_file_types,
                        :max_file_size_mb,
                        :verification_required,
                        :created_at
                    )
                """),
                {
                    "service_id": service_id,
                    "document_name": document_name,
                    "description": description,
                    "is_mandatory": True,
                    "accepted_formats": "PDF,JPG,JPEG,PNG",
                    "accepted_file_types": "application/pdf,image/jpeg,image/png",
                    "max_file_size_mb": 5,
                    "verification_required": True,
                    "created_at": now,
                },
            )

        db.commit()

        print("SUCCESS")
        print(f"Scholarship service ID: {scholarship}")
        print(f"Income Certificate service ID: {income}")
        print("Demo service requirements inserted successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed()