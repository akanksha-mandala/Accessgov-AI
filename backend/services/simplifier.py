import logging
from typing import Dict, Any
from schemas.requirement import SimpleExplanationResponse

logger = logging.getLogger("accessgov.services.simplifier")

# Dictionary of government jargon definitions and citizen-friendly translations
TERMS_DICTIONARY: Dict[str, Dict[str, Any]] = {
    "domicile certificate": {
        "simple_explanation": "Proof that you permanently live in a state.",
        "key_points": [
            "Confirms your permanent address in the state.",
            "Needed for state government job reservations and college admissions.",
            "Issued by the Revenue Department / Tahsildar."
        ],
        "why_it_matters": "Proves state residency so you receive local citizen scheme benefits."
    },
    "income certificate": {
        "simple_explanation": "Official proof of how much money your family earns in a year.",
        "key_points": [
            "Shows total annual earning from salary, agriculture, or business.",
            "Required to qualify for fee concessions and scholarships.",
            "Valid for 1 financial year."
        ],
        "why_it_matters": "Helps government determine if your family qualifies for low-income welfare programs."
    },
    "community certificate": {
        "simple_explanation": "Official paper confirming your caste or community category.",
        "key_points": [
            "Confirms membership in SC, ST, OBC, BC, or EWS categories.",
            "Unlocks educational reservations, age relaxation, and fee waivers.",
            "Permanent document valid for lifetime."
        ],
        "why_it_matters": "Ensures social welfare and reservation benefits reach eligible communities."
    },
    "udid card": {
        "simple_explanation": "National identity card for persons with disabilities.",
        "key_points": [
            "Contains unique 18-digit disability identification number.",
            "Grants bus/rail travel concessions and monthly government pensions.",
            "Replaces paper medical board certificates nationwide."
        ],
        "why_it_matters": "One single digital card for accessing all disability schemes across India."
    },
    "bonafide certificate": {
        "simple_explanation": "School or college letter proving you are a current active student.",
        "key_points": [
            "Issued on official school/college letterhead with principal seal.",
            "Proves course enrollment and academic year details.",
            "Required when applying for student scholarships or bus passes."
        ],
        "why_it_matters": "Verifies active student status before scholarship funds are disbursed."
    }
}


class TerminologySimplifierService:
    """
    Government Terminology Simplifier Service.
    Converts complex administrative legal terms into plain, citizen-friendly explanations.
    """

    @staticmethod
    def simplify_term(term: str, language: str = "en") -> SimpleExplanationResponse:
        """
        Translates official government terminology into simple language with key bullet points.
        """
        term_clean = term.strip().lower()

        # Lookup in pre-configured terminology dictionary
        for key, data in TERMS_DICTIONARY.items():
            if key in term_clean or term_clean in key:
                return SimpleExplanationResponse(
                    original_term=term,
                    simple_explanation=data["simple_explanation"],
                    key_points=data["key_points"],
                    why_it_matters=data["why_it_matters"],
                    language=language
                )

        # Default fallback structure for unlisted administrative terms
        return SimpleExplanationResponse(
            original_term=term,
            simple_explanation=f"Official government document or procedure: '{term}'.",
            key_points=[
                f"Required administrative document for public service processing.",
                "Obtainable from your local Revenue Department, e-Seva, or Municipal Office.",
                "Usually verified alongside your primary identity proof (Aadhaar Card)."
            ],
            why_it_matters="Ensures legal compliance and identity verification for public service delivery.",
            language=language
        )


simplifier_service = TerminologySimplifierService()
