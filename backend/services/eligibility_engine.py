import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from schemas.eligibility import EligibilityCheckRequest, EligibilityResult
import crud.crud_service as crud_service
import crud.crud_requirement as crud_requirement


logger = logging.getLogger("accessgov.services.eligibility_engine")


class RuleBasedEligibilityEngine:
    """
    Deterministic eligibility engine for AccessGov AI.

    Service-specific rules:

    1. Tamil Nadu BC/MBC/DNC/OBC Post-Matric Scholarship profile
       - Student status required
       - Supported community category required
       - Tamil Nadu required
       - Annual parental income <= Rs. 2,50,000
       - Academic marks are recorded but are NOT treated as a
         universal mandatory eligibility threshold for this scheme.

    2. Income Certificate
       - No income ceiling.
       - Academic marks are irrelevant.
       - Income information is required for the profile.
       - Supporting documents determine document readiness.

    3. Existing pension/disability rules are retained.
    """

    SCHOLARSHIP_INCOME_LIMIT = 250000.0

    # The actual TN BC/MBC/DNC scholarship profile is based on
    # BC/MBC/DNC community eligibility. OBC is retained here because
    # the existing AccessGov UI uses OBC as a selectable category.
    SCHOLARSHIP_CATEGORIES = {"BC", "MBC", "DNC", "OBC"}

    # ------------------------------------------------------------------
    # Service identification
    # ------------------------------------------------------------------

    @staticmethod
    def _is_scholarship(
        service_title: Optional[str],
        service_code: Optional[str]
    ) -> bool:
        title = (service_title or "").strip().lower()
        code = (service_code or "").strip().upper()

        return (
            "scholarship" in title
            or "scholarship" in code.lower()
            or code.startswith("SCH")
        )

    @staticmethod
    def _is_income_certificate(
        service_title: Optional[str],
        service_code: Optional[str]
    ) -> bool:
        title = (service_title or "").strip().lower()
        code = (service_code or "").strip().upper()

        return (
            "income certificate" in title
            or code == "INCOME_CERTIFICATE"
        )

    @staticmethod
    def _normalise_category(category: Optional[str]) -> str:
        return (category or "").strip().upper()

    # ------------------------------------------------------------------
    # Service resolution
    # ------------------------------------------------------------------

    @staticmethod
    def _resolve_service(
        db: Session,
        request: EligibilityCheckRequest
    ):
        """
        Resolve the service as reliably as possible.

        Frontend currently sends both service_id and service_code.
        Prefer service_id when it resolves, but fall back to service_code.
        """

        service = None

        # First try service_id.
        if request.service_id is not None:
            try:
                service = crud_service.get_service_by_id(
                    db,
                    request.service_id
                )
            except Exception as exc:
                logger.warning(
                    "Service lookup by ID failed for %s: %s",
                    request.service_id,
                    exc
                )

        # If ID did not resolve, try service_code.
        if service is None and request.service_code:
            try:
                service = crud_service.get_service_by_code(
                    db,
                    request.service_code
                )
            except Exception as exc:
                logger.warning(
                    "Service lookup by code failed for %s: %s",
                    request.service_code,
                    exc
                )

        return service

    # ------------------------------------------------------------------
    # Document matching
    # ------------------------------------------------------------------

    @staticmethod
    def _document_matches(
        required_document: str,
        uploaded_documents: List[str]
    ) -> bool:
        required = required_document.strip().lower()

        for uploaded in uploaded_documents:
            uploaded_normalised = uploaded.strip().lower()

            if (
                required in uploaded_normalised
                or uploaded_normalised in required
            ):
                return True

        return False

    # ------------------------------------------------------------------
    # Main evaluation
    # ------------------------------------------------------------------

    @staticmethod
    def evaluate_eligibility(
        db: Session,
        request: EligibilityCheckRequest
    ) -> EligibilityResult:

        # ==============================================================
        # 1. Resolve service
        # ==============================================================

        service = RuleBasedEligibilityEngine._resolve_service(
            db,
            request
        )

        # Use the database service when available.
        #
        # If the DB lookup fails but the frontend supplied a known
        # service_code, the supplied code is still used so the correct
        # service-specific rule can execute.

        service_title = (
            service.title
            if service
            else "Requested Government Service"
        )

        service_code = (
            service.code
            if service
            else (request.service_code or "")
        )

        processing_days = (
            service.processing_days
            if service
            else 7
        )

        # ==============================================================
        # 2. Determine service type
        # ==============================================================

        scholarship = RuleBasedEligibilityEngine._is_scholarship(
            service_title,
            service_code
        )

        income_certificate = RuleBasedEligibilityEngine._is_income_certificate(
            service_title,
            service_code
        )

        # Important fallback:
        # If the DB service was resolved but its title/code is unexpected,
        # trust the explicit frontend service_code when it identifies one
        # of the known flagship services.

        if not scholarship and not income_certificate:
            request_code = (request.service_code or "").strip().upper()

            if request_code.startswith("SCH") or request_code == "SCHOLARSHIP":
                scholarship = True

            elif request_code == "INCOME_CERTIFICATE":
                income_certificate = True

        logger.info(
            "Eligibility evaluation: service_id=%s, service_code=%s, "
            "service_title=%s, scholarship=%s, income_certificate=%s",
            request.service_id,
            request.service_code,
            service_title,
            scholarship,
            income_certificate
        )

        # ==============================================================
        # 3. Required documents
        # ==============================================================

        req_docs = (
            crud_requirement.get_requirement_documents(
                db,
                service.id
            )
            if service
            else []
        )

        # Fallback document lists for the flagship services.

        if not req_docs:

            if scholarship:
                req_docs = [
                    "Aadhaar Card",
                    "Community Certificate",
                    "Income Certificate",
                    "Student ID / Bonafide Certificate",
                    "Passport Photograph",
                ]

            elif income_certificate:
                req_docs = [
                    "Applicant Photo",
                    "Address Proof",
                    "Family / Smart Card",
                    "Self Declaration",
                    "Income Supporting Document",
                    "Latest Salary Certificate",
                    "PAN Card",
                ]

            else:
                req_docs = [
                    "Aadhaar Card",
                    "Income Certificate",
                    "Passport Photograph",
                ]

        # ==============================================================
        # 4. Initialise evaluation
        # ==============================================================

        matched_rules: List[str] = []
        disqualifications: List[str] = []
        missing_conditions: List[str] = []
        missing_documents: List[str] = []
        next_steps: List[str] = []

        applicable_conditions = 0
        met_conditions = 0

        category = RuleBasedEligibilityEngine._normalise_category(
            request.caste_category
        )

        state = (request.state or "").strip().lower()

        # ==============================================================
        # 5. SCHOLARSHIP RULES
        # ==============================================================

        if scholarship:

            # ----------------------------------------------------------
            # Student status
            # ----------------------------------------------------------

            applicable_conditions += 1

            student = bool(
                request.is_student
                or (
                    request.occupation
                    and request.occupation.strip().lower() == "student"
                )
            )

            if student:
                met_conditions += 1

                matched_rules.append(
                    "Applicant is identified as a student."
                )

            else:
                disqualifications.append(
                    "Student status is required for the post-matric scholarship."
                )

            # ----------------------------------------------------------
            # Community
            # ----------------------------------------------------------

            applicable_conditions += 1

            if category in RuleBasedEligibilityEngine.SCHOLARSHIP_CATEGORIES:
                met_conditions += 1

                matched_rules.append(
                    f"Community category ({request.caste_category}) "
                    "matches the supported scholarship profile."
                )

            else:
                disqualifications.append(
                    "Applicant category does not match the supported "
                    "BC/MBC/DNC scholarship profile."
                )

            # ----------------------------------------------------------
            # State
            # ----------------------------------------------------------

            applicable_conditions += 1

            if state == "tamil nadu":
                met_conditions += 1

                matched_rules.append(
                    "Applicant state is Tamil Nadu."
                )

            else:
                disqualifications.append(
                    "This AccessGov AI scholarship profile is configured "
                    "for Tamil Nadu applicants."
                )

            # ----------------------------------------------------------
            # Annual parental income
            # ----------------------------------------------------------

            applicable_conditions += 1

            if request.annual_income is None:

                missing_conditions.append(
                    "Annual parental income is required."
                )

            elif request.annual_income <= (
                RuleBasedEligibilityEngine.SCHOLARSHIP_INCOME_LIMIT
            ):

                met_conditions += 1

                matched_rules.append(
                    "Annual parental income "
                    f"(Rs. {request.annual_income:,.0f}) is within the "
                    "Rs. 2,50,000 scholarship income ceiling."
                )

            else:

                # IMPORTANT:
                # Do NOT also add "Annual income recorded..." as a
                # matched rule here. This is a disqualifying condition.

                disqualifications.append(
                    "Annual parental income exceeds the "
                    "Rs. 2,50,000 ceiling for this post-matric "
                    "scholarship profile."
                )

            # ----------------------------------------------------------
            # Academic marks
            # ----------------------------------------------------------

            if request.marks is not None:

                matched_rules.append(
                    f"Academic score recorded: {request.marks:.1f}%."
                )

                matched_rules.append(
                    "Academic marks are recorded for scholarship "
                    "profile/selection context and are not treated "
                    "as a universal mandatory eligibility threshold "
                    "for this scheme profile."
                )

            else:

                # Marks are informational for this scheme profile,
                # therefore absence of marks does NOT disqualify the
                # applicant.

                matched_rules.append(
                    "Academic score was not provided; no universal "
                    "marks threshold is applied by this scheme profile."
                )

        # ==============================================================
        # 6. INCOME CERTIFICATE RULES
        # ==============================================================

        elif income_certificate:

            # ----------------------------------------------------------
            # State
            # ----------------------------------------------------------

            applicable_conditions += 1

            if state == "tamil nadu":

                met_conditions += 1

                matched_rules.append(
                    "Applicant state is Tamil Nadu."
                )

            else:

                disqualifications.append(
                    "This Income Certificate service profile "
                    "is configured for Tamil Nadu."
                )

            # ----------------------------------------------------------
            # Income
            # ----------------------------------------------------------

            applicable_conditions += 1

            if request.annual_income is not None:

                met_conditions += 1

                matched_rules.append(
                    f"Declared annual income recorded as "
                    f"Rs. {request.annual_income:,.0f}; "
                    "no income ceiling is applied to the Income "
                    "Certificate service."
                )

            else:

                missing_conditions.append(
                    "Declared income information is required."
                )

            # ----------------------------------------------------------
            # Academic marks
            # ----------------------------------------------------------

            if request.marks is not None:

                matched_rules.append(
                    f"Academic score ({request.marks:.1f}%) recorded "
                    "but not used for Income Certificate eligibility."
                )

        # ==============================================================
        # 7. EXISTING PENSION RULES
        # ==============================================================

        elif (
            "PEN" in service_code.upper()
            or "pension" in service_title.lower()
        ):

            applicable_conditions += 1

            if request.age is None:

                missing_conditions.append(
                    "Age details are required."
                )

            elif "old age" in service_title.lower():

                if request.age >= 60:

                    met_conditions += 1

                    matched_rules.append(
                        f"Age ({request.age}) meets the 60-year requirement."
                    )

                else:

                    disqualifications.append(
                        "Minimum age requirement of 60 years is not met."
                    )

            else:

                met_conditions += 1

                matched_rules.append(
                    f"Age ({request.age}) recorded for pension evaluation."
                )

        # ==============================================================
        # 8. EXISTING DISABILITY RULE
        # ==============================================================

        elif (
            "DIS" in service_code.upper()
            or "disability" in service_title.lower()
        ):

            applicable_conditions += 1

            disability = request.disability_percentage or 0

            if disability >= 40:

                met_conditions += 1

                matched_rules.append(
                    f"Disability percentage ({disability:.0f}%) "
                    "meets the 40% benchmark."
                )

            else:

                disqualifications.append(
                    "A minimum certified disability benchmark "
                    "of 40% is required for this service profile."
                )

        # ==============================================================
        # 9. Generic service
        # ==============================================================

        else:

            logger.warning(
                "No service-specific eligibility rule matched for "
                "service_title=%s, service_code=%s",
                service_title,
                service_code
            )

            if request.state:

                applicable_conditions += 1
                met_conditions += 1

                matched_rules.append(
                    f"Applicant state recorded as {request.state}."
                )

            if request.annual_income is not None:

                applicable_conditions += 1
                met_conditions += 1

                matched_rules.append(
                    f"Annual income recorded as "
                    f"Rs. {request.annual_income:,.0f}."
                )

        # ==============================================================
        # 10. Document readiness
        # ==============================================================

        uploaded = request.uploaded_document_types or []

        uploaded_count = 0

        for required_document in req_docs:

            if RuleBasedEligibilityEngine._document_matches(
                required_document,
                uploaded
            ):

                uploaded_count += 1

            else:

                missing_documents.append(
                    required_document
                )

        document_readiness = (
            (uploaded_count / len(req_docs)) * 100.0
            if req_docs
            else 100.0
        )

        document_readiness = round(
            document_readiness,
            1
        )

        # ==============================================================
        # 11. Eligibility score
        # ==============================================================

        if applicable_conditions > 0:

            eligibility_score = (
                met_conditions / applicable_conditions
            ) * 100.0

        else:

            eligibility_score = 0.0

        eligibility_score = round(
            eligibility_score,
            1
        )

        # ==============================================================
        # 12. Determine eligibility status
        # ==============================================================

        if disqualifications:

            eligible = False
            eligibility_status = "Not Eligible"

        elif missing_conditions:

            eligible = True
            eligibility_status = "Partially Eligible"

        elif missing_documents:

            eligible = True
            eligibility_status = "Partially Eligible"

        else:

            eligible = True
            eligibility_status = "Eligible"

        # ==============================================================
        # 13. Application readiness
        # ==============================================================

        readiness_score = round(
            (
                eligibility_score * 0.6
            )
            +
            (
                document_readiness * 0.4
            ),
            1
        )

        # A disqualified applicant must never appear application-ready.
        if disqualifications:

            readiness_score = min(
                readiness_score,
                40.0
            )

        # ==============================================================
        # 14. Next steps
        # ==============================================================

        if disqualifications:

            next_steps.append(
                "Review the eligibility conditions that were not satisfied."
            )

        if missing_conditions:

            next_steps.append(
                "Provide or correct the missing profile information."
            )

        if missing_documents:

            next_steps.append(
                "Upload missing required documents: "
                + ", ".join(missing_documents[:5])
                + "."
            )

        if (
            eligible
            and not missing_conditions
            and not missing_documents
        ):

            next_steps.append(
                "Application profile appears complete for this "
                "eligibility check. Final verification is performed "
                "by the competent government authority."
            )

        # ==============================================================
        # 15. Return structured result
        # ==============================================================

        return EligibilityResult(
            eligible=eligible,
            eligibility_status=eligibility_status,
            eligibility_score=eligibility_score,
            readiness_score=readiness_score,
            required_documents=req_docs,
            missing_documents=missing_documents,
            missing_conditions=missing_conditions,
            next_steps=next_steps,
            estimated_processing_days=processing_days,
            matched_rules=matched_rules,
            disqualification_reasons=disqualifications,
        )


eligibility_engine = RuleBasedEligibilityEngine()
