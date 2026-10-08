import time
import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from schemas.agent import (
    ConversationRequest,
    ConversationResponse,
)
from agents.session_manager import session_manager
from agents.intent_router import intent_router
from agents.adk_config import adk_config

import crud.crud_service as crud_service
import crud.crud_requirement as crud_requirement


logger = logging.getLogger("accessgov.agents.conversation_agent")


class ConversationAgent:

    DEMO_SERVICE_CODES = {
        "SCHOLARSHIP",
        "INCOME_CERTIFICATE",
    }

    LANGUAGE_NAMES = {
        "en": "English",
        "ta": "Tamil",
        "te": "Telugu",
        "hi": "Hindi",
        "kn": "Kannada",
    }

    DEMO_APPLICATION_GUIDANCE = {
        "SCHOLARSHIP": {
            "application_page": (
                "Scholarship application page in the Citizen Dashboard"
            ),
            "navigation": [
                "Open the Citizen Dashboard.",
                "Open Services.",
                "Select Scholarship.",
                "Review eligibility and required documents.",
                "Upload the required documents in the Document Vault if needed.",
                "Open the Scholarship application page.",
                "Fill in the application details.",
                "Review the information and submit the application.",
            ],
            "note": (
                "This is a prototype workflow for the AccessGov AI demo. "
                "It does not submit an application to a real government department."
            ),
        },
        "INCOME_CERTIFICATE": {
            "application_page": (
                "Income Certificate application page in the Citizen Dashboard"
            ),
            "navigation": [
                "Open the Citizen Dashboard.",
                "Open Services.",
                "Select Income Certificate.",
                "Review eligibility and required documents.",
                "Upload the required documents in the Document Vault if needed.",
                "Open the Income Certificate application page.",
                "Fill in the application details.",
                "Review the information and submit the application.",
            ],
            "note": (
                "This is a prototype workflow for the AccessGov AI demo. "
                "It does not submit an application to a real government department."
            ),
        },
    }

    # ================================================================
    # FALLBACK TRANSLATIONS
    # ================================================================

    DOCUMENT_TRANSLATIONS = {
        "en": {
            "aadhaar card": "Aadhaar Card",
            "student id or bonafide certificate": (
                "Student ID or Bonafide Certificate"
            ),
            "income certificate": "Income Certificate",
            "bank account details": "Bank Account Details",
            "passport photograph": "Passport Photograph",
            "bank passbook": "Bank Passbook",
            "ration card": "Ration Card",
            "community certificate": "Community Certificate",
        },
        "te": {
            "aadhaar card": "ఆధార్ కార్డు",
            "student id or bonafide certificate": (
                "విద్యార్థి గుర్తింపు కార్డు లేదా బోనఫైడ్ సర్టిఫికేట్"
            ),
            "income certificate": "ఆదాయ ధృవీకరణ పత్రం",
            "bank account details": "బ్యాంక్ ఖాతా వివరాలు",
            "passport photograph": "పాస్‌పోర్ట్ ఫోటో",
            "bank passbook": "బ్యాంక్ పాస్‌బుక్",
            "ration card": "రేషన్ కార్డు",
            "community certificate": "సామాజిక వర్గ ధృవీకరణ పత్రం",
        },
        "ta": {
            "aadhaar card": "ஆதார் அட்டை",
            "student id or bonafide certificate": (
                "மாணவர் அடையாள அட்டை அல்லது போனஃபைடு சான்றிதழ்"
            ),
            "income certificate": "வருமானச் சான்றிதழ்",
            "bank account details": "வங்கி கணக்கு விவரங்கள்",
            "passport photograph": "பாஸ்போர்ட் புகைப்படம்",
            "bank passbook": "வங்கி பாஸ்புக்",
            "ration card": "குடும்ப அட்டை",
            "community certificate": "சமூகச் சான்றிதழ்",
        },
        "hi": {
            "aadhaar card": "आधार कार्ड",
            "student id or bonafide certificate": (
                "छात्र पहचान पत्र या बोनाफाइड प्रमाण पत्र"
            ),
            "income certificate": "आय प्रमाण पत्र",
            "bank account details": "बैंक खाता विवरण",
            "passport photograph": "पासपोर्ट फोटो",
            "bank passbook": "बैंक पासबुक",
            "ration card": "राशन कार्ड",
            "community certificate": "सामुदायिक प्रमाण पत्र",
        },
        "kn": {
            "aadhaar card": "ಆಧಾರ್ ಕಾರ್ಡ್",
            "student id or bonafide certificate": (
                "ವಿದ್ಯಾರ್ಥಿ ಗುರುತಿನ ಚೀಟಿ ಅಥವಾ ಬೋನಫೈಡ್ ಪ್ರಮಾಣಪತ್ರ"
            ),
            "income certificate": "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ",
            "bank account details": "ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರಗಳು",
            "passport photograph": "ಪಾಸ್‌ಪೋರ್ಟ್ ಫೋಟೋ",
            "bank passbook": "ಬ್ಯಾಂಕ್ ಪಾಸ್‌ಬುಕ್",
            "ration card": "ಪಡಿತರ ಚೀಟಿ",
            "community certificate": "ಸಮುದಾಯ ಪ್ರಮಾಣಪತ್ರ",
        },
    }

    SERVICE_TRANSLATIONS = {
        "SCHOLARSHIP": {
            "en": "Scholarship",
            "te": "విద్యార్థి వేతనం",
            "ta": "உதவித்தொகை",
            "hi": "छात्रवृत्ति",
            "kn": "ವಿದ್ಯಾರ್ಥಿವೇತನ",
        },
        "INCOME_CERTIFICATE": {
            "en": "Income Certificate",
            "te": "ఆదాయ ధృవీకరణ పత్రం",
            "ta": "வருமானச் சான்றிதழ்",
            "hi": "आय प्रमाण पत्र",
            "kn": "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ",
        },
    }

    ELIGIBILITY_TRANSLATIONS = {
        "SCHOLARSHIP": {
            "te": (
                "ఈ డెమో కోసం విద్యార్థులు తమ విద్యార్థి స్థితిని "
                "మరియు సంబంధిత స్కాలర్‌షిప్ పథకానికి వర్తించే "
                "అర్హత నిబంధనలను పరిశీలించాలి."
            ),
            "ta": (
                "இந்த டெமோவில், மாணவர்கள் தங்கள் மாணவர் நிலை "
                "மற்றும் குறிப்பிட்ட உதவித்தொகை திட்டத்திற்கான "
                "தகுதி நிபந்தனைகளை சரிபார்க்க வேண்டும்."
            ),
            "hi": (
                "इस डेमो के लिए छात्रों को अपनी छात्र स्थिति और "
                "संबंधित छात्रवृत्ति योजना की पात्रता शर्तों की "
                "जाँच करनी चाहिए।"
            ),
            "kn": (
                "ಈ ಡೆಮೊಗಾಗಿ ವಿದ್ಯಾರ್ಥಿಗಳು ತಮ್ಮ ವಿದ್ಯಾರ್ಥಿ ಸ್ಥಿತಿ "
                "ಮತ್ತು ಸಂಬಂಧಿತ ವಿದ್ಯಾರ್ಥಿವೇತನ ಯೋಜನೆಯ ಅರ್ಹತಾ "
                "ನಿಯಮಗಳನ್ನು ಪರಿಶೀಲಿಸಬೇಕು."
            ),
        },
        "INCOME_CERTIFICATE": {
            "te": (
                "ఈ డెమో కోసం ఆదాయ ధృవీకరణ పత్రానికి వర్తించే "
                "అర్హత మరియు ఆదాయ సంబంధిత నిబంధనలను పరిశీలించాలి."
            ),
            "ta": (
                "இந்த டெமோவில் வருமானச் சான்றிதழுக்கான தகுதி "
                "மற்றும் வருமானம் தொடர்பான விதிகளை சரிபார்க்க வேண்டும்."
            ),
            "hi": (
                "इस डेमो में आय प्रमाण पत्र के लिए लागू पात्रता "
                "और आय संबंधी नियमों की जाँच करनी चाहिए।"
            ),
            "kn": (
                "ಈ ಡೆಮೊದಲ್ಲಿ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರಕ್ಕೆ ಅನ್ವಯಿಸುವ ಅರ್ಹತೆ "
                "ಮತ್ತು ಆದಾಯ ಸಂಬಂಧಿತ ನಿಯಮಗಳನ್ನು ಪರಿಶೀಲಿಸಬೇಕು."
            ),
        },
    }

    # ================================================================
    # MAIN CONVERSATION PROCESSING
    # ================================================================

    def process_citizen_request(
        self,
        db: Session,
        request: ConversationRequest,
        user_id: Optional[int] = None,
    ) -> ConversationResponse:

        start_time = time.time()

        try:
            session_id = (
                request.session_id
                or f"session_{int(time.time())}"
            )

            session_manager.get_or_create_session(
                session_id
            )

            session_manager.add_message(
                session_id=session_id,
                role="user",
                content=request.message,
            )

            # --------------------------------------------------------
            # Build service knowledge
            # --------------------------------------------------------

            knowledge = self._build_demo_knowledge(db)

            # --------------------------------------------------------
            # Detect intent
            # --------------------------------------------------------

            intent_prediction = intent_router.classify_intent(
                request.message,
            )

            # --------------------------------------------------------
            # Detect service
            # --------------------------------------------------------

            suggested_service = self._detect_service(
                request.message,
                knowledge,
            )

            # --------------------------------------------------------
            # Retrieve conversation history
            # --------------------------------------------------------

            history = []

            try:
                session_history = session_manager.get_messages(
                    session_id
                )

                if session_history:
                    history = session_history

            except Exception as history_error:
                logger.warning(
                    "Unable to retrieve conversation history: %s",
                    history_error,
                )

            # --------------------------------------------------------
            # Build ONE Gemini prompt
            # --------------------------------------------------------

            prompt = self._build_gemini_prompt(
                user_message=request.message,
                language=request.language,
                history=history,
                knowledge=knowledge,
                page_context=request.page_context,
            )

            # --------------------------------------------------------
            # ONE Gemini request only
            #
            # Important:
            # Do NOT call another Gemini request just to translate
            # the result. Gemini is already instructed to answer in
            # the selected language.
            # --------------------------------------------------------

            final_text = None

            try:
                final_text = (
                    adk_config.generate_content_with_retry(
                        prompt
                    )
                )
            except Exception as gemini_error:
                logger.warning(
                    "Gemini generation failed; using deterministic "
                    "fallback: %s",
                    gemini_error,
                )

            # --------------------------------------------------------
            # Deterministic fallback if Gemini unavailable
            # --------------------------------------------------------

            if not final_text or not final_text.strip():

                logger.warning(
                    "Gemini returned no response. "
                    "Using deterministic multilingual fallback."
                )

                final_text = self._fallback_response(
                    request.message,
                    request.language,
                    knowledge,
                )

            final_text = final_text.strip()

            # --------------------------------------------------------
            # Save assistant message
            # --------------------------------------------------------

            session_manager.add_message(
                session_id=session_id,
                role="assistant",
                content=final_text,
            )

            processing_time = (
                time.time() - start_time
            )

            return ConversationResponse(
                response=final_text,
                detected_intent=intent_prediction.intent,
                confidence=intent_prediction.confidence,
                conversation_session_id=session_id,
                suggested_service=suggested_service,
                sources_used=[
                    {
                        "source": (
                            "PostgreSQL demo service catalog"
                        )
                    }
                ],
                response_time_ms=round(
                    processing_time * 1000
                ),
            )

        except Exception as exc:

            logger.error(
                "Conversation processing failed: %s",
                str(exc),
                exc_info=True,
            )

            fallback = self._fallback_response(
                request.message,
                request.language,
                [],
            )

            return ConversationResponse(
                response=fallback,
                detected_intent="general",
                confidence=0.0,
                conversation_session_id=(
                    request.session_id or ""
                ),
                suggested_service=None,
                sources_used=[],
                response_time_ms=round(
                    (time.time() - start_time) * 1000
                ),
            )

    # ================================================================
    # BUILD DEMO KNOWLEDGE
    # ================================================================

    def _build_demo_knowledge(
        self,
        db: Session,
    ) -> list[Dict[str, Any]]:

        services = crud_service.get_all_services(
            db,
            limit=100,
        )

        knowledge = []

        for service in services:

            code = (
                str(service.code or "")
                .upper()
                .replace("-", "_")
                .replace(" ", "_")
            )

            title = str(
                service.title or ""
            ).lower()

            is_scholarship = (
                "scholar" in code.lower()
                or "scholarship" in title
            )

            is_income = (
                "income" in code.lower()
                or "income" in title
            )

            if not (
                is_scholarship
                or is_income
            ):
                continue

            requirements = (
                crud_requirement.get_service_requirements(
                    db,
                    service.id,
                )
            )

            required_documents = []

            for requirement in requirements or []:

                document_name = getattr(
                    requirement,
                    "document_name",
                    None,
                )

                if document_name:
                    required_documents.append(
                        document_name
                    )

            demo_code = (
                "SCHOLARSHIP"
                if is_scholarship
                else "INCOME_CERTIFICATE"
            )

            guidance = (
                self.DEMO_APPLICATION_GUIDANCE[
                    demo_code
                ]
            )

            knowledge.append(
                {
                    "service_id": service.id,
                    "code": demo_code,
                    "title": service.title,
                    "category": service.category,
                    "department": (
                        getattr(
                            service,
                            "department_name",
                            None,
                        )
                        or getattr(
                            service,
                            "department",
                            None,
                        )
                    ),
                    "description": service.description,
                    "eligibility": (
                        service.eligibility_criteria
                    ),
                    "required_documents": (
                        required_documents
                    ),
                    "required_documents_summary": (
                        service.required_documents_summary
                    ),
                    "processing_time_days": (
                        service.processing_time_days
                    ),
                    "fee": service.fee_amount,
                    "validity_period": (
                        service.validity_period
                    ),
                    "available_online": (
                        service.available_online
                    ),
                    "state": service.state,
                    "application_page": (
                        guidance["application_page"]
                    ),
                    "application_steps": (
                        guidance["navigation"]
                    ),
                    "demo_note": (
                        guidance["note"]
                    ),
                }
            )

        return knowledge

    # ================================================================
    # GEMINI PROMPT
    # ================================================================

    def _build_gemini_prompt(
        self,
        user_message: str,
        language: str,
        history: list,
        knowledge: list[Dict[str, Any]],
        page_context: Optional[str] = None,
    ) -> str:

        language = (
            language or "en"
        ).lower().strip()

        language_name = self.LANGUAGE_NAMES.get(
            language,
            "English",
        )

        knowledge_text = self._safe_json(
            knowledge
        )

        history_text = self._safe_json(
            history[-12:]
        )

        return f"""
You are the AccessGov AI citizen assistant.

You are having a natural, conversational interaction with a citizen.

SELECTED LANGUAGE:
{language_name} ({language})

============================================================
LANGUAGE REQUIREMENT
============================================================

Your entire answer MUST be written naturally in {language_name}.

Do NOT answer in another language.

Do NOT mix English with the selected language unless:
- the product name "AccessGov AI" is being used, or
- a proper name, URL, official code, or unavoidable document name
  has no natural translation.

Translate ordinary service and interface terms naturally.

Examples:

Scholarship:
- Telugu: విద్యార్థి వేతనం
- Tamil: உதவித்தொகை
- Hindi: छात्रवृत्ति
- Kannada: ವಿದ್ಯಾರ್ಥಿವೇತನ

Income Certificate:
- Telugu: ఆదాయ ధృవీకరణ పత్రం
- Tamil: வருமானச் சான்றிதழ்
- Hindi: आय प्रमाण पत्र
- Kannada: ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ

Citizen Dashboard:
- Translate naturally into the selected language.

Services:
- Translate naturally into the selected language.

Document Vault:
- Translate naturally into the selected language.

Application:
- Translate naturally into the selected language.

Required documents:
- Translate naturally into the selected language.

Eligibility:
- Translate naturally into the selected language.

IMPORTANT:
Do not produce a sentence that begins in the selected language
and then switches to English or another Indian language.

============================================================
NATURAL CONVERSATION
============================================================

Do NOT behave like a rigid FAQ system.

Understand what the citizen is actually asking.

For example:

If the citizen says:
"Scholarship"

Give a useful short explanation of the scholarship service
and invite a relevant follow-up.

If the citizen says:
"How do I apply for scholarship?"

Give the application process.

If the citizen says:
"What documents are needed?"

Give the required documents.

If the citizen says:
"Am I eligible?"

Give eligibility information.

If the citizen says:
"Where should I apply?"

Explain where to navigate in the AccessGov AI prototype.

If the citizen asks a follow-up such as:
"What about documents?"
use the previous conversation context to understand that
they are referring to the service already being discussed.

Do NOT repeatedly ask which service they mean when the service
is already obvious from the conversation.

============================================================
DEMO SCOPE
============================================================

This AccessGov AI prototype currently provides detailed
guidance for:

1. Scholarship
2. Income Certificate

Do not invent unsupported government services or policies.

============================================================
APPLICATION WORKFLOW
============================================================

The prototype application workflow is:

Citizen Dashboard
→ Services
→ Select the service
→ Review eligibility and required documents
→ Document Vault if documents are needed
→ Open the service application page
→ Fill application details
→ Review
→ Submit

This is a prototype workflow.

NEVER claim that AccessGov AI submitted a real government
application.

NEVER claim that a real government department received an
application through this prototype.

============================================================
FACTUAL SOURCE
============================================================

The PostgreSQL service catalog below is the source of truth for:

- eligibility
- required documents
- fees
- processing time
- service description
- department
- availability

Do not invent factual values.

The supplied application workflow is valid demo guidance.

============================================================
CURRENT PAGE
============================================================

{page_context or "Not provided"}

============================================================
SERVICE KNOWLEDGE
============================================================

{knowledge_text}

============================================================
RECENT CONVERSATION
============================================================

{history_text}

============================================================
USER MESSAGE
============================================================

{user_message}

============================================================
RESPONSE STYLE
============================================================

- Answer the actual question directly.
- Be natural and conversational.
- Keep responses understandable for citizens with low literacy.
- Use numbered steps for procedures.
- Use bullets for document lists.
- Do not mention Gemini.
- Do not mention APIs.
- Do not mention databases.
- Do not mention prompts.
- Do not mention internal implementation.
- Do not say you are an AI model.
- Do not repeat the same generic response for different questions.
- Maintain conversation context.
- Answer completely in {language_name}.
""".strip()

    # ================================================================
    # SERVICE DETECTION
    # ================================================================

    def _detect_service(
        self,
        message: str,
        knowledge: list[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:

        message_lower = (
            message or ""
        ).lower().strip()

        scholarship_aliases = [
            "scholarship",
            "student scholarship",
            "scholar",
            "స్కాలర్షిప్",
            "షాలర్షిప్",
            "స్కాలర్‌షిప్",
            "స్కాలర్ షిప్",
            "విద్యార్థి వేతనం",
            "स्कॉलरशिप",
            "स्कालरशिप",
            "छात्रवृत्ति",
            "छात्रवृति",
            "ஸ்காலர்ஷிப்",
            "உதவித்தொகை",
            "மாணவர் உதவித்தொகை",
            "ಸ್ಕಾಲರ್‌ಶಿಪ್",
            "ಸ್ಕಾಲರ್ಶಿಪ್",
            "ವಿದ್ಯಾರ್ಥಿವೇತನ",
            "ವಿದ್ಯಾರ್ಥಿ ವೇತನ",
        ]

        income_certificate_aliases = [
            "income certificate",
            "income",
            "ఆదాయ సర్టిఫికేట్",
            "ఆదాయ సర్టిఫికెట్",
            "ఇన్‌కమ్ సర్టిఫికేట్",
            "ఇన్కమ్ సర్టిఫికేట్",
            "ఆదాయ ధృవీకరణ పత్రం",
            "आय प्रमाण पत्र",
            "आय प्रमाणपत्र",
            "इनकम सर्टिफिकेट",
            "வருமானச் சான்றிதழ்",
            "வருமான சான்றிதழ்",
            "ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ",
            "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ",
        ]

        for item in knowledge:

            title = str(
                item.get("title", "")
            ).lower()

            code = str(
                item.get("code", "")
            ).lower()

            if (
                any(
                    alias.lower()
                    in message_lower
                    for alias in scholarship_aliases
                )
                and (
                    "scholar" in title
                    or "scholar" in code
                    or code == "scholarship"
                )
            ):

                return item

            if (
                any(
                    alias.lower()
                    in message_lower
                    for alias in income_certificate_aliases
                )
                and (
                    "income" in title
                    or "income" in code
                    or code == "income_certificate"
                )
            ):

                return item

        for item in knowledge:

            title = str(
                item.get("title", "")
            ).lower()

            code = str(
                item.get("code", "")
            ).lower()

            if code and code in message_lower:
                return item

            if title and title in message_lower:
                return item

        return None

    # ================================================================
    # LOCALIZED SERVICE NAME
    # ================================================================

    def _localized_service_name(
        self,
        service: Dict[str, Any],
        language: str,
    ) -> str:

        language = (
            language or "en"
        ).lower().strip()

        code = str(
            service.get("code", "")
        ).upper()

        translations = self.SERVICE_TRANSLATIONS.get(
            code
        )

        if translations:
            return translations.get(
                language,
                translations["en"],
            )

        return str(
            service.get("title")
            or "Service"
        )

    # ================================================================
    # LOCALIZED DOCUMENT NAME
    # ================================================================

    def _localized_document_name(
        self,
        document: Any,
        language: str,
    ) -> str:

        original = str(
            document or ""
        ).strip()

        if not original:
            return ""

        normalized = (
            original.lower()
            .replace("–", "-")
            .replace("—", "-")
        )

        translations = self.DOCUMENT_TRANSLATIONS.get(
            language,
            self.DOCUMENT_TRANSLATIONS["en"],
        )

        if normalized in translations:
            return translations[normalized]

        # Handle common variations.
        if "aadhaar" in normalized:
            return translations.get(
                "aadhaar card",
                original,
            )

        if (
            "bonafide" in normalized
            or "student id" in normalized
        ):
            return translations.get(
                "student id or bonafide certificate",
                original,
            )

        if "income certificate" in normalized:
            return translations.get(
                "income certificate",
                original,
            )

        if "bank" in normalized and (
            "account" in normalized
            or "details" in normalized
        ):
            return translations.get(
                "bank account details",
                original,
            )

        if (
            "passport" in normalized
            and "photo" in normalized
        ):
            return translations.get(
                "passport photograph",
                original,
            )

        return original

    # ================================================================
    # LOCALIZED DOCUMENT LIST
    # ================================================================

    def _localized_documents(
        self,
        documents: list,
        language: str,
    ) -> list[str]:

        result = []

        for document in documents:

            localized = self._localized_document_name(
                document,
                language,
            )

            if localized:
                result.append(localized)

        return result

    # ================================================================
    # LOCALIZED ELIGIBILITY
    # ================================================================

    def _localized_eligibility(
        self,
        service: Dict[str, Any],
        language: str,
    ) -> str:

        language = (
            language or "en"
        ).lower().strip()

        code = str(
            service.get("code", "")
        ).upper()

        if language == "en":

            return str(
                service.get("eligibility")
                or "Eligibility information is not currently available."
            )

        translations = (
            self.ELIGIBILITY_TRANSLATIONS.get(
                code,
                {},
            )
        )

        if language in translations:
            return translations[language]

        return (
            "இந்த தகவல் தற்போது கிடைக்கவில்லை."
            if language == "ta"
            else (
                "ఈ సమాచారం ప్రస్తుతం అందుబాటులో లేదు."
                if language == "te"
                else (
                    "यह जानकारी वर्तमान में उपलब्ध नहीं है।"
                    if language == "hi"
                    else (
                        "ಈ ಮಾಹಿತಿ ಪ್ರಸ್ತುತ ಲಭ್ಯವಿಲ್ಲ."
                        if language == "kn"
                        else str(
                            service.get("eligibility")
                            or "Eligibility information is not currently available."
                        )
                    )
                )
            )
        )

    # ================================================================
    # DETERMINISTIC FALLBACK
    # ================================================================

    def _fallback_response(
        self,
        message: str,
        language: str,
        knowledge: list[Dict[str, Any]],
    ) -> str:

        language = (
            language or "en"
        ).lower().strip()

        message_lower = (
            message or ""
        ).lower().strip()

        service = self._detect_service(
            message,
            knowledge,
        )

        # ------------------------------------------------------------
        # Intent keywords
        # ------------------------------------------------------------

        application_keywords = [
            "how to apply",
            "how do i apply",
            "apply",
            "application process",
            "application procedure",
            "process",
            "steps",
            "where to apply",
            "how can i apply",
            "application",
            "దరఖాస్తు",
            "ఎలా దరఖాస్తు",
            "అప్లై",
            "ప్రాసెస్",
            "దరఖాస్తు చేయాలి",
            "దరఖాస్తు విధానం",
            "விண்ணப்பிக்க",
            "எப்படி விண்ணப்பிக்க",
            "விண்ணப்ப செயல்முறை",
            "விண்ணப்பம்",
            "விண்ணப்பிக்கும் முறை",
            "कैसे आवेदन",
            "आवेदन कैसे",
            "आवेदन प्रक्रिया",
            "आवेदन",
            "ಅರ್ಜಿ",
            "ಹೇಗೆ ಅರ್ಜಿ",
            "ಅರ್ಜಿ ಸಲ್ಲಿಸುವ",
            "ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆ",
        ]

        document_keywords = [
            "document",
            "documents",
            "required document",
            "required documents",
            "what should i upload",
            "what to upload",
            "papers",
            "upload",
            "పత్రాలు",
            "అవసరమైన పత్రాలు",
            "ఏ పత్రాలు",
            "డాక్యుమెంట్లు",
            "అప్‌లోడ్",
            "ஆவணங்கள்",
            "தேவையான ஆவணங்கள்",
            "என்ன ஆவணங்கள்",
            "பதிவேற்ற",
            "दस्तावेज",
            "दस्तावेज़",
            "आवश्यक दस्तावेज",
            "अपलोड",
            "ದಾಖಲೆಗಳು",
            "ಅಗತ್ಯ ದಾಖಲೆಗಳು",
            "ಯಾವ ದಾಖಲೆ",
            "ಅಪ್‌ಲೋಡ್",
        ]

        eligibility_keywords = [
            "eligible",
            "eligibility",
            "who can apply",
            "am i eligible",
            "qualification",
            "qualify",
            "தகுதி",
            "தகுதியான",
            "தகுதி என்ன",
            "எனக்கு தகுதி",
            "ఎవరు అర్హులు",
            "అర్హత",
            "అర్హుడిని",
            "అర్హత ఏమిటి",
            "पात्रता",
            "कौन आवेदन कर सकता",
            "पात्र",
            "ಅರ್ಹತೆ",
            "ಯಾರು ಅರ್ಜಿ",
            "ಅರ್ಹರಾಗಿದ್ದೇನೆ",
        ]

        application_intent = any(
            keyword in message_lower
            for keyword in application_keywords
        )

        document_intent = any(
            keyword in message_lower
            for keyword in document_keywords
        )

        eligibility_intent = any(
            keyword in message_lower
            for keyword in eligibility_keywords
        )

        # ------------------------------------------------------------
        # If service is known
        # ------------------------------------------------------------

        if service:

            title = self._localized_service_name(
                service,
                language,
            )

            required_documents = (
                service.get(
                    "required_documents",
                    [],
                )
                or []
            )

            localized_documents = (
                self._localized_documents(
                    required_documents,
                    language,
                )
            )

            localized_eligibility = (
                self._localized_eligibility(
                    service,
                    language,
                )
            )

            # ========================================================
            # TELUGU
            # ========================================================

            if language == "te":

                if application_intent:

                    return (
                        f"{title} కోసం దరఖాస్తు చేయడానికి "
                        "ఈ దశలను అనుసరించండి:\n\n"
                        "1. పౌరుల డ్యాష్‌బోర్డ్‌ను తెరవండి.\n"
                        "2. సేవల విభాగాన్ని తెరవండి.\n"
                        f"3. {title} సేవను ఎంచుకోండి.\n"
                        "4. అర్హత మరియు అవసరమైన పత్రాలను పరిశీలించండి.\n"
                        "5. అవసరమైన పత్రాలను డాక్యుమెంట్ వాల్ట్‌లో "
                        "అప్‌లోడ్ చేయండి.\n"
                        "6. దరఖాస్తు పేజీని తెరవండి.\n"
                        "7. దరఖాస్తు వివరాలను నమోదు చేయండి.\n"
                        "8. వివరాలను పరిశీలించి దరఖాస్తును సమర్పించండి.\n\n"
                        "ఇది AccessGov AI డెమోలోని నమూనా దరఖాస్తు విధానం. "
                        "ఇది నిజమైన ప్రభుత్వ దరఖాస్తును సమర్పించదు."
                    )

                if document_intent:

                    if localized_documents:

                        return (
                            f"{title} కోసం అవసరమైన పత్రాలు:\n\n"
                            + "\n".join(
                                f"• {doc}"
                                for doc in localized_documents
                            )
                            + "\n\n"
                            "ఈ పత్రాలను డాక్యుమెంట్ వాల్ట్‌లో "
                            "అప్‌లోడ్ చేయవచ్చు."
                        )

                    return (
                        f"{title} కోసం అవసరమైన పత్రాల పూర్తి జాబితా "
                        "ప్రస్తుతం ఈ డెమోలో అందుబాటులో లేదు."
                    )

                if eligibility_intent:

                    return (
                        f"{title} అర్హత సమాచారం:\n\n"
                        f"{localized_eligibility}"
                    )

                response = (
                    f"{title} సేవ గురించి మీకు సమాచారం అందించగలను.\n\n"
                )

                if localized_eligibility:
                    response += (
                        f"అర్హత: {localized_eligibility}\n\n"
                    )

                if localized_documents:

                    response += (
                        "అవసరమైన పత్రాలు:\n"
                        + "\n".join(
                            f"• {doc}"
                            for doc in localized_documents
                        )
                        + "\n\n"
                    )

                response += (
                    "మీకు దరఖాస్తు విధానం, అర్హత లేదా "
                    "అవసరమైన పత్రాల గురించి అడగవచ్చు."
                )

                return response

            # ========================================================
            # TAMIL
            # ========================================================

            if language == "ta":

                if application_intent:

                    return (
                        f"{title} விண்ணப்பிக்க இந்த "
                        "படிகளைப் பின்பற்றவும்:\n\n"
                        "1. குடிமக்கள் டாஷ்போர்டைத் திறக்கவும்.\n"
                        "2. சேவைகள் பகுதியைத் திறக்கவும்.\n"
                        f"3. {title} சேவையைத் தேர்ந்தெடுக்கவும்.\n"
                        "4. தகுதி மற்றும் தேவையான ஆவணங்களைப் பார்க்கவும்.\n"
                        "5. தேவையான ஆவணங்களை ஆவணக் களஞ்சியத்தில் பதிவேற்றவும்.\n"
                        "6. விண்ணப்பப் பக்கத்தைத் திறக்கவும்.\n"
                        "7. விண்ணப்ப விவரங்களை நிரப்பவும்.\n"
                        "8. விவரங்களைச் சரிபார்த்து விண்ணப்பத்தைச் சமர்ப்பிக்கவும்.\n\n"
                        "இது AccessGov AI டெமோவின் மாதிரி விண்ணப்ப நடைமுறை. "
                        "இது உண்மையான அரசு விண்ணப்பத்தைச் சமர்ப்பிக்காது."
                    )

                if document_intent:

                    if localized_documents:

                        return (
                            f"{title} க்கு தேவையான ஆவணங்கள்:\n\n"
                            + "\n".join(
                                f"• {doc}"
                                for doc in localized_documents
                            )
                            + "\n\n"
                            "இந்த ஆவணங்களை ஆவணக் களஞ்சியத்தில் "
                            "பதிவேற்றலாம்."
                        )

                    return (
                        f"{title} க்கான தேவையான ஆவணங்களின் "
                        "முழுமையான பட்டியல் தற்போது கிடைக்கவில்லை."
                    )

                if eligibility_intent:

                    return (
                        f"{title} தகுதி தகவல்:\n\n"
                        f"{localized_eligibility}"
                    )

                return (
                    f"{title} சேவை பற்றிய தகவலை வழங்க முடியும்.\n\n"
                    "விண்ணப்ப நடைமுறை, தகுதி அல்லது தேவையான "
                    "ஆவணங்கள் பற்றி கேட்கலாம்."
                )

            # ========================================================
            # HINDI
            # ========================================================

            if language == "hi":

                if application_intent:

                    return (
                        f"{title} के लिए आवेदन करने के चरण:\n\n"
                        "1. नागरिक डैशबोर्ड खोलें।\n"
                        "2. सेवाएँ खोलें।\n"
                        f"3. {title} सेवा चुनें।\n"
                        "4. पात्रता और आवश्यक दस्तावेज़ देखें।\n"
                        "5. आवश्यक दस्तावेज़ दस्तावेज़ वॉल्ट में अपलोड करें।\n"
                        "6. आवेदन पृष्ठ खोलें।\n"
                        "7. आवेदन विवरण भरें।\n"
                        "8. जानकारी की समीक्षा करके आवेदन जमा करें।\n\n"
                        "यह AccessGov AI डेमो की नमूना आवेदन प्रक्रिया है। "
                        "यह वास्तविक सरकारी आवेदन जमा नहीं करता है।"
                    )

                if document_intent:

                    if localized_documents:

                        return (
                            f"{title} के लिए आवश्यक दस्तावेज़:\n\n"
                            + "\n".join(
                                f"• {doc}"
                                for doc in localized_documents
                            )
                            + "\n\n"
                            "इन दस्तावेज़ों को दस्तावेज़ वॉल्ट में "
                            "अपलोड किया जा सकता है।"
                        )

                    return (
                        f"{title} के आवश्यक दस्तावेज़ों की पूरी सूची "
                        "वर्तमान डेमो में उपलब्ध नहीं है।"
                    )

                if eligibility_intent:

                    return (
                        f"{title} की पात्रता जानकारी:\n\n"
                        f"{localized_eligibility}"
                    )

                return (
                    f"{title} सेवा के बारे में मैं जानकारी दे सकता हूँ।\n\n"
                    "आप आवेदन प्रक्रिया, पात्रता या आवश्यक दस्तावेज़ों "
                    "के बारे में पूछ सकते हैं।"
                )

            # ========================================================
            # KANNADA
            # ========================================================

            if language == "kn":

                if application_intent:

                    return (
                        f"{title} ಗೆ ಅರ್ಜಿ ಸಲ್ಲಿಸಲು "
                        "ಈ ಹಂತಗಳನ್ನು ಅನುಸರಿಸಿ:\n\n"
                        "1. ನಾಗರಿಕ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ ತೆರೆಯಿರಿ.\n"
                        "2. ಸೇವೆಗಳ ವಿಭಾಗ ತೆರೆಯಿರಿ.\n"
                        f"3. {title} ಸೇವೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ.\n"
                        "4. ಅರ್ಹತೆ ಮತ್ತು ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಪರಿಶೀಲಿಸಿ.\n"
                        "5. ಅಗತ್ಯ ದಾಖಲೆಗಳನ್ನು ಡಾಕ್ಯುಮೆಂಟ್ ವಾಲ್ಟ್‌ಗೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ.\n"
                        "6. ಅರ್ಜಿ ಪುಟ ತೆರೆಯಿರಿ.\n"
                        "7. ಅರ್ಜಿ ವಿವರಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ.\n"
                        "8. ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ ಅರ್ಜಿಯನ್ನು ಸಲ್ಲಿಸಿ.\n\n"
                        "ಇದು AccessGov AI ಡೆಮೊದ ಮಾದರಿ ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆಯಾಗಿದೆ. "
                        "ಇದು ನಿಜವಾದ ಸರ್ಕಾರಿ ಅರ್ಜಿಯನ್ನು ಸಲ್ಲಿಸುವುದಿಲ್ಲ."
                    )

                if document_intent:

                    if localized_documents:

                        return (
                            f"{title} ಗೆ ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳು:\n\n"
                            + "\n".join(
                                f"• {doc}"
                                for doc in localized_documents
                            )
                            + "\n\n"
                            "ಈ ದಾಖಲೆಗಳನ್ನು ಡಾಕ್ಯುಮೆಂಟ್ ವಾಲ್ಟ್‌ಗೆ "
                            "ಅಪ್‌ಲೋಡ್ ಮಾಡಬಹುದು."
                        )

                    return (
                        f"{title} ಗೆ ಅಗತ್ಯವಿರುವ ದಾಖಲೆಗಳ ಸಂಪೂರ್ಣ ಪಟ್ಟಿ "
                        "ಪ್ರಸ್ತುತ ಡೆಮೊದಲ್ಲಿ ಲಭ್ಯವಿಲ್ಲ."
                    )

                if eligibility_intent:

                    return (
                        f"{title} ಅರ್ಹತಾ ಮಾಹಿತಿ:\n\n"
                        f"{localized_eligibility}"
                    )

                return (
                    f"{title} ಸೇವೆಯ ಬಗ್ಗೆ ಮಾಹಿತಿ ನೀಡಬಹುದು.\n\n"
                    "ಅರ್ಜಿ ಪ್ರಕ್ರಿಯೆ, ಅರ್ಹತೆ ಅಥವಾ ಅಗತ್ಯ ದಾಖಲೆಗಳ "
                    "ಬಗ್ಗೆ ಕೇಳಬಹುದು."
                )

            # ========================================================
            # ENGLISH
            # ========================================================

            if application_intent:

                return (
                    f"Here is how to apply for {title}:\n\n"
                    "1. Open the Citizen Dashboard.\n"
                    "2. Open Services.\n"
                    f"3. Select {title}.\n"
                    "4. Review the eligibility and required documents.\n"
                    "5. Upload the required documents to the Document Vault if needed.\n"
                    "6. Open the application page.\n"
                    "7. Fill in the application details.\n"
                    "8. Review the information and submit the application.\n\n"
                    "This is the prototype workflow in the AccessGov AI demo. "
                    "It does not submit a real government application."
                )

            if document_intent:

                if localized_documents:

                    return (
                        f"Required documents for {title}:\n\n"
                        + "\n".join(
                            f"• {doc}"
                            for doc in localized_documents
                        )
                    )

                return (
                    f"The complete required-document list for {title} "
                    "is not currently available in this demo."
                )

            if eligibility_intent:

                return (
                    f"Eligibility information for {title}:\n\n"
                    f"{localized_eligibility}"
                )

            return (
                f"I can help you with {title}. "
                "You can ask about the application process, "
                "eligibility, or required documents."
            )

        # ============================================================
        # NO SERVICE DETECTED
        # ============================================================

        if language == "te":

            return (
                "ఈ AccessGov AI డెమోలో విద్యార్థి వేతనం మరియు "
                "ఆదాయ ధృవీకరణ పత్రం సేవలకు మార్గదర్శకత్వం "
                "అందుబాటులో ఉంది. మీరు ఏ సేవ గురించి "
                "తెలుసుకోవాలనుకుంటున్నారు?"
            )

        if language == "ta":

            return (
                "இந்த AccessGov AI டெமோவில் உதவித்தொகை மற்றும் "
                "வருமானச் சான்றிதழ் சேவைகளுக்கான வழிகாட்டுதல் "
                "கிடைக்கிறது. நீங்கள் எந்த சேவையைப் பற்றி "
                "தெரிந்துகொள்ள விரும்புகிறீர்கள்?"
            )

        if language == "hi":

            return (
                "इस AccessGov AI डेमो में छात्रवृत्ति और "
                "आय प्रमाण पत्र सेवाओं के लिए मार्गदर्शन "
                "उपलब्ध है। आप किस सेवा के बारे में "
                "जानना चाहते हैं?"
            )

        if language == "kn":

            return (
                "ಈ AccessGov AI ಡೆಮೊದಲ್ಲಿ ವಿದ್ಯಾರ್ಥಿವೇತನ ಮತ್ತು "
                "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ ಸೇವೆಗಳಿಗೆ ಮಾರ್ಗದರ್ಶನ ಲಭ್ಯವಿದೆ. "
                "ನೀವು ಯಾವ ಸೇವೆಯ ಬಗ್ಗೆ ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೀರಿ?"
            )

        return (
            "This AccessGov AI demo provides guidance for "
            "Scholarship and Income Certificate services. "
            "Which service would you like help with?"
        )

    # ================================================================
    # SAFE JSON
    # ================================================================

    @staticmethod
    def _safe_json(
        value: Any,
    ) -> str:

        import json

        try:

            return json.dumps(
                value,
                ensure_ascii=False,
                indent=2,
                default=str,
            )

        except Exception:

            return str(value)


conversation_agent = ConversationAgent()