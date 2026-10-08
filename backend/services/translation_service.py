import json
import logging
from typing import Dict
from urllib.parse import quote
from urllib.request import Request, urlopen

from agents.adk_config import adk_config

logger = logging.getLogger("accessgov.services.translation")

SUPPORTED_LANGUAGES = ["en", "ta", "te", "hi", "kn"]

LANGUAGE_NAMES = {
    "en": "English",
    "ta": "Tamil",
    "te": "Telugu",
    "hi": "Hindi",
    "kn": "Kannada",
}

TRANSLATION_LOOKUP: Dict[str, Dict[str, str]] = {
    "welcome_message": {
        "en": "Welcome to AccessGov AI. How can I assist you with government services today?",
        "ta": "அக்சஸ்கவ் AI-க்கு நல்வரவு. இன்று அரசு சேவைகளில் உங்களுக்கு நான் எவ்வாறு உதவ முடியும்?",
        "te": "AccessGov AIకి స్వాగతం. ఈరోజు ప్రభుత్వ సేవలతో నేను మీకు ఎలా సహాయం చేయగలను?",
        "hi": "AccessGov AI में आपका स्वागत है। आज मैं सरकारी सेवाओं में आपकी क्या सहायता कर सकता हूँ?",
        "kn": "AccessGov AI ಗೆ ಸ್ವಾಗತ. ಇಂದು ಸರ್ಕಾರಿ ಸೇವೆಗಳಲ್ಲಿ ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    },
}


class TranslationService:
    """
    Translate assistant-generated or page content into the citizen's
    selected language.

    Known platform messages use deterministic translations.
    Arbitrary text first uses Gemini/ADK and then falls back to
    Google's public translation endpoint when Gemini is unavailable.
    """

    def __init__(self):
        self.supported_languages = SUPPORTED_LANGUAGES

    def _normalize_language(self, language: str) -> str:
        language = (language or "en").lower().strip()

        aliases = {
            "en-us": "en",
            "en-in": "en",
            "ta-in": "ta",
            "te-in": "te",
            "hi-in": "hi",
            "kn-in": "kn",
        }

        return aliases.get(language, language)

    def _lookup_translation(
        self,
        text: str,
        target_lang: str,
    ) -> str | None:
        normalized_text = " ".join(text.strip().split())

        for language_dict in TRANSLATION_LOOKUP.values():
            for source_language, source_text in language_dict.items():
                if source_language != "en":
                    continue

                if " ".join(source_text.strip().split()) == normalized_text:
                    return language_dict.get(target_lang)

        return None

    def _translate_with_public_service(
        self,
        text: str,
        source: str,
        target: str,
    ) -> str | None:
        """
        Fallback translation for page-reader text.

        This uses Google's public translation endpoint so that the
        Page Reader can continue working when the configured Gemini
        quota is unavailable.
        """

        if not text.strip():
            return text

        if source == target:
            return text

        translated_parts = []

        # Keep requests reasonably small for the public endpoint.
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                translated_parts.append("")
                continue

            chunks = [
                paragraph[index:index + 900]
                for index in range(0, len(paragraph), 900)
            ]

            translated_chunks = []

            for chunk in chunks:
                url = (
                    "https://translate.googleapis.com/"
                    "translate_a/single"
                    "?client=gtx"
                    f"&sl={quote(source)}"
                    f"&tl={quote(target)}"
                    "&dt=t"
                    f"&q={quote(chunk)}"
                )

                request = Request(
                    url,
                    headers={
                        "User-Agent": "AccessGov-AI/1.0",
                    },
                )

                try:
                    with urlopen(
                        request,
                        timeout=10,
                    ) as response:
                        payload = json.loads(
                            response.read().decode("utf-8")
                        )

                    segments = payload[0]

                    translated_chunk = "".join(
                        segment[0]
                        for segment in segments
                        if segment and segment[0]
                    )

                    if translated_chunk.strip():
                        translated_chunks.append(
                            translated_chunk
                        )
                    else:
                        return None

                except Exception as exc:
                    logger.warning(
                        "Public translation failed for %s -> %s: %s",
                        source,
                        target,
                        exc,
                    )
                    return None

            translated_parts.append(
                " ".join(translated_chunks).strip()
            )

        result = "\n".join(translated_parts).strip()

        return result if result else None

    def translate_text(
        self,
        text: str,
        target_lang: str = "en",
        source_lang: str = "en",
    ) -> str:
        if not text or not text.strip():
            return text

        target = self._normalize_language(target_lang)
        source = self._normalize_language(source_lang)

        if target not in self.supported_languages:
            logger.warning(
                "Unsupported target language '%s'; "
                "falling back to English.",
                target_lang,
            )
            target = "en"

        if source not in self.supported_languages:
            source = "en"

        if target == source:
            return text

        # Deterministic translations first.
        fixed_translation = self._lookup_translation(
            text,
            target,
        )

        if fixed_translation:
            return fixed_translation

        source_name = LANGUAGE_NAMES.get(
            source,
            "English",
        )

        target_name = LANGUAGE_NAMES.get(
            target,
            "English",
        )

        prompt = f"""
Translate the following text from {source_name} into {target_name}.

Requirements:
- Preserve the exact meaning.
- Do not add facts, explanations, warnings, or commentary.
- Preserve numbers exactly.
- Preserve government service names and service codes.
- Preserve document names where appropriate.
- Preserve URLs exactly.
- Preserve bullet points and list structure.
- Preserve headings and line breaks where possible.
- Use natural, respectful language appropriate for an Indian citizen.
- Do not transliterate unless that is the normal writing system of the target language.
- Return ONLY the translated text.

TEXT:
{text}
""".strip()

        # Primary translation: configured Gemini/ADK service.
        try:
            translated = (
                adk_config.generate_content_with_retry(
                    prompt
                )
            )

            if translated and translated.strip():
                return translated.strip()

            logger.warning(
                "Gemini returned an empty translation for %s -> %s.",
                source,
                target,
            )

        except Exception as exc:
            logger.warning(
                "Gemini translation failed for %s -> %s: %s",
                source,
                target,
                exc,
            )

        # Fallback translation so Page Reader does not speak
        # the original English text with a foreign voice.
        fallback_translation = (
            self._translate_with_public_service(
                text,
                source,
                target,
            )
        )

        if fallback_translation:
            return fallback_translation

        # If every translator fails, return the original text.
        # The caller can decide whether it is safe to speak it.
        logger.error(
            "All translation methods failed for %s -> %s.",
            source,
            target,
        )

        return text


translation_service = TranslationService()