import logging
from functools import wraps
from typing import Optional

from config import settings

logger = logging.getLogger("accessgov.agents.adk_config")


class ADKConfig:
    """
    Gemini configuration for AccessGov AI.

    One Gemini request is made per citizen message.
    Gemini handles natural-language conversation and multilingual
    responses while backend data remains the factual source of truth.
    """

    def __init__(self):
        self.model_name = settings.GEMINI_MODEL or "gemini-2.5-flash"
        self.api_key = settings.GEMINI_API_KEY
        self.temperature = 0.2
        self._client = None

    def initialize_genai(self):
        """Initialize the current Google GenAI Python client."""
        if self._client is not None:
            return self._client

        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY is not configured. "
                "Gemini responses will be unavailable."
            )
            return None

        try:
            from google import genai

            self._client = genai.Client(
                api_key=self.api_key
            )

            logger.info(
                "Gemini client initialized successfully using model '%s'.",
                self.model_name
            )

            return self._client

        except Exception as exc:
            logger.error(
                "Could not initialize Gemini client: %s",
                exc
            )
            self._client = None
            return None

    def generate_content_with_retry(
        self,
        prompt: str
    ) -> Optional[str]:
        """
        Generate exactly one Gemini response for a citizen message.

        Retries are intentionally limited so a failed API call does not
        create another 20-40 second chatbot delay.
        """

        client = self.initialize_genai()

        if client is None:
            return None

        try:
            response = client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={
                    "temperature": self.temperature,
                }
            )

            if response and getattr(response, "text", None):
                return response.text.strip()

            logger.warning("Gemini returned an empty response.")
            return None

        except Exception as exc:
            logger.error(
                "Gemini generation failed: %s",
                exc,
                exc_info=True
            )
            return None


adk_config = ADKConfig()