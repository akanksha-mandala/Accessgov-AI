import logging
from typing import Dict, Tuple

from schemas.agent import IntentPrediction
from agents.adk_config import adk_config

logger = logging.getLogger("accessgov.agents.intent_router")


KEYWORD_INTENT_MAP = {
    "service_discovery": [
        # English
        "need", "want", "find", "search", "looking for", "services",
        "scheme", "catalog", "available", "recommend", "apply for",
        "scholarship", "income certificate", "open", "show me",
        "find scholarship", "find income certificate",

        # Telugu
        "స్కాలర్షిప్", "షాలర్షిప్", "స్కాలర్‌షిప్",
        "స్కాలర్ షిప్", "ทุน",  # harmless fallback token
        "సేవ", "పథకం", "కావాలి", "వెతుకు", "దరఖాస్తు",

        # Hindi
        "स्कॉलरशिप", "स्कालरशिप", "छात्रवृत्ति",
        "छात्रवृति", "योजना", "सेवा", "चाहिए",
        "आवेदन", "ढूंढ", "खोज",

        # Tamil
        "ஸ்காலர்ஷிப்", "ஸ்காலர்ஷிப் வேண்டும்",
        "உதவித்தொகை", "உதவித்தொகை வேண்டும்",
        "திட்டம்", "சேவை", "வேண்டும்",
        "விண்ணப்பம்", "தேட",

        # Kannada
        "ಸ್ಕಾಲರ್‌ಶಿಪ್", "ಸ್ಕಾಲರ್ಶಿಪ್",
        "ವಿದ್ಯಾರ್ಥಿವೇತನ", "ಯೋಜನೆ", "ಸೇವೆ",
        "ಬೇಕು", "ಅರ್ಜಿ", "ಹುಡುಕು",
    ],

    "eligibility_check": [
        # English
        "eligible", "eligibility", "can i get", "qualify",
        "am i eligible", "income limit", "age limit",
        "criteria", "can a student", "can senior citizen",
        "who can apply",

        # Telugu
        "అర్హత", "అర్హుడా", "అర్హత ఉందా", "ఎవరు దరఖాస్తు",
        "అర్హులు", "అర్హతలు",

        # Hindi
        "पात्र", "पात्रता", "क्या मैं पात्र", "कौन आवेदन",
        "योग्यता", "अर्हता",

        # Tamil
        "தகுதி", "தகுதியா", "யார் விண்ணப்பிக்கலாம்",
        "தகுதிகள்",

        # Kannada
        "ಅರ್ಹತೆ", "ಅರ್ಹರಾಗಿದ್ದೇನೆ", "ಯಾರು ಅರ್ಜಿ",
        "ಅರ್ಹರು",
    ],

    "document_requirements": [
        # English
        "document", "documents", "proof", "what do i need",
        "required", "bring", "upload", "papers", "attach",
        "file format", "which documents", "what documents do i need",

        # Telugu
        "పత్రాలు", "డాక్యుమెంట్", "డాక్యుమెంట్లు",
        "ఏ పత్రాలు", "ఏ డాక్యుమెంట్లు", "అవసరమైన పత్రాలు",
        "అప్‌లోడ్",

        # Hindi
        "दस्तावेज", "दस्तावेज़", "कौन से दस्तावेज",
        "जरूरी दस्तावेज", "कागजात", "अपलोड",

        # Tamil
        "ஆவணம்", "ஆவணங்கள்", "என்ன ஆவணங்கள்",
        "தேவையான ஆவணங்கள்", "பதிவேற்ற",

        # Kannada
        "ದಾಖಲೆ", "ದಾಖಲೆಗಳು", "ಯಾವ ದಾಖಲೆಗಳು",
        "ಅಗತ್ಯ ದಾಖಲೆಗಳು", "ಅಪ್‌ಲೋಡ್",
    ],

    "simple_explanation": [
        # English
        "explain", "what is", "meaning of", "simple language",
        "in tamil", "in hindi", "in telugu", "dont understand",
        "what means",

        # Telugu
        "వివరించండి", "అర్థం ఏమిటి", "సులభంగా", "అర్థం కాలేదు",

        # Hindi
        "समझाइए", "मतलब क्या है", "आसान भाषा", "समझ नहीं आया",

        # Tamil
        "விளக்கவும்", "என்ன அர்த்தம்", "எளிமையாக", "புரியவில்லை",

        # Kannada
        "ವಿವರಿಸಿ", "ಅರ್ಥ ಏನು", "ಸರಳವಾಗಿ", "ಅರ್ಥವಾಗಲಿಲ್ಲ",
    ],

    "application_guidance": [
        # English
        "how to apply", "steps", "procedure", "where to apply",
        "e-seva", "online portal", "processing time", "fee",
        "how long", "next step", "save my progress",
        "save progress", "continue my application",
        "resume my application",

        # Telugu
        "ఎలా దరఖాస్తు", "దరఖాస్తు ఎలా", "దశలు",
        "తదుపరి దశ", "ఎక్కడ దరఖాస్తు",

        # Hindi
        "आवेदन कैसे", "कैसे आवेदन करें", "चरण",
        "अगला कदम", "कहां आवेदन",

        # Tamil
        "எப்படி விண்ணப்பிப்பது", "விண்ணப்பிப்பது எப்படி",
        "படிகள்", "அடுத்த படி", "எங்கே விண்ணப்பிக்க",

        # Kannada
        "ಅರ್ಜಿ ಹೇಗೆ", "ಹೇಗೆ ಅರ್ಜಿ", "ಹಂತಗಳು",
        "ಮುಂದಿನ ಹಂತ", "ಎಲ್ಲಿ ಅರ್ಜಿ",
    ],

    "greeting": [
        "hi", "hello", "namaste", "vanakkam", "namaskaram",
        "good morning", "good evening", "hey",

        # Telugu
        "నమస్కారం", "హలో", "హాయ్",

        # Hindi
        "नमस्ते", "नमस्कार", "हैलो", "हाय",

        # Tamil
        "வணக்கம்", "ஹலோ", "ஹாய்",

        # Kannada
        "ನಮಸ್ಕಾರ", "ಹಲೋ", "ಹಾಯ್",
    ],
}


class IntentRouter:
    def __init__(self, confidence_threshold: float = 0.70):
        self.threshold = confidence_threshold

    def classify_intent(self, text: str) -> IntentPrediction:
        if not text or not text.strip():
            return IntentPrediction(
                intent="unknown",
                confidence=0.0,
                method="rule_empty"
            )

        text_lower = text.lower().strip()
                # Native Unicode service detection
        native_service_keywords = [
            # Telugu
            "స్కాలర్షిప్",
            "షాలర్షిప్",
            "స్కాలర్‌షిప్",
            "స్కాలర్ షిప్",
            "విద్యార్థి వేతనం",
            "ఆదాయ సర్టిఫికేట్",
            "ఇన్‌కమ్ సర్టిఫికేట్",

            # Hindi
            "स्कॉलरशिप",
            "स्कालरशिप",
            "छात्रवृत्ति",
            "आय प्रमाण पत्र",
            "इनकम सर्टिफिकेट",

            # Tamil
            "ஸ்காலர்ஷிப்",
            "உதவித்தொகை",
            "மாணவர் உதவித்தொகை",
            "வருமானச் சான்றிதழ்",
            "வருமான சான்றிதழ்",

            # Kannada
            "ಸ್ಕಾಲರ್‌ಶಿಪ್",
            "ಸ್ಕಾಲರ್ಶಿಪ್",
            "ವಿದ್ಯಾರ್ಥಿವೇತನ",
            "ವಿದ್ಯಾರ್ಥಿ ವೇತನ",
            "ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ",
            "ಆದಾಯ ಪ್ರಮಾಣಪತ್ರ",
        ]

        for keyword in native_service_keywords:
            if keyword.lower() in text_lower:
                logger.info(
                    "Native Unicode service keyword matched: '%s'",
                    keyword
                )
                return IntentPrediction(
                    intent="service_discovery",
                    confidence=0.95,
                    method="native_unicode_rules"
                )

        # Exact greeting
        if text_lower in KEYWORD_INTENT_MAP["greeting"]:
            return IntentPrediction(
                intent="greeting",
                confidence=0.95,
                method="keyword_rules"
            )

        scores: Dict[str, float] = {
            intent: 0.0
            for intent in KEYWORD_INTENT_MAP
        }

        for intent, keywords in KEYWORD_INTENT_MAP.items():
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    scores[intent] += 1.0

        best_intent = max(scores, key=scores.get)
        max_hits = scores[best_intent]

        if max_hits > 0:
            confidence = min(
                0.90,
                0.50 + (max_hits * 0.20)
            )

            if confidence >= self.threshold:
                logger.info(
                    "Stage 1 multilingual rule classifier matched "
                    "intent '%s' with confidence %.2f",
                    best_intent,
                    confidence
                )

                return IntentPrediction(
                    intent=best_intent,
                    confidence=confidence,
                    method="multilingual_keyword_rules"
                )

        # Gemini remains only as a fallback for genuinely ambiguous queries.
        logger.info(
            "Stage 1 confidence below threshold. "
            "Invoking Stage 2 Gemini fallback classifier..."
        )

        llm_intent, llm_conf = self._gemini_classify_fallback(text)

        return IntentPrediction(
            intent=llm_intent,
            confidence=llm_conf,
            method="llm_fallback"
        )

    def _gemini_classify_fallback(
        self,
        text: str
    ) -> Tuple[str, float]:

        prompt = (
            "Classify the following citizen query into EXACTLY ONE "
            "intent category:\n"
            "Categories: [service_discovery, eligibility_check, "
            "document_requirements, simple_explanation, "
            "application_guidance, greeting, unknown]\n\n"
            f'Query: "{text}"\n\n'
            "Reply with ONLY the category name."
        )

        try:
            response_text = adk_config.generate_content_with_retry(prompt)

            if response_text:
                predicted = response_text.strip().lower()

                for valid_intent in KEYWORD_INTENT_MAP.keys():
                    if valid_intent in predicted:
                        return valid_intent, 0.85

                if "unknown" in predicted:
                    return "unknown", 0.60

        except Exception as exc:
            logger.warning(
                "Stage 2 Gemini fallback classification failed (%s). "
                "Returning unknown fallback.",
                exc
            )

        return "unknown", 0.50


intent_router = IntentRouter()

