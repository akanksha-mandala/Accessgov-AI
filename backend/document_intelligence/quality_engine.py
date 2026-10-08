import logging
import os
from typing import List, Dict, Any

import cv2

logger = logging.getLogger("accessgov.document_intelligence.quality_engine")


class DocumentQualityEngine:
    """
    Genuine physical document-quality inspection.

    Checks:
    - Image resolution
    - Blur / sharpness
    - Brightness / exposure
    - Blank or near-blank images
    - Basic visual quality

    This is separate from OCR confidence:
        Quality = can the image itself be reliably inspected?
        OCR = how confidently can text be extracted?
    """

    # These are intentionally conservative demo thresholds.
    MIN_WIDTH = 700
    MIN_HEIGHT = 700

    # Laplacian variance thresholds.
    # Higher = sharper image.
    VERY_BLURRY = 40.0
    LOW_SHARPNESS = 80.0

    MIN_NON_BLANK_RATIO = 0.02

    MIN_BRIGHTNESS = 35.0
    MAX_BRIGHTNESS = 225.0

    @staticmethod
    def inspect_image(image_path: str) -> Dict[str, Any]:
        """
        Inspect an image and return deterministic quality metrics.
        """

        if not image_path or not os.path.exists(image_path):
            return {
                "readable": False,
                "quality_score": 0.0,
                "sharpness_score": 0.0,
                "brightness_score": 0.0,
                "resolution_score": 0.0,
                "non_blank_ratio": 0.0,
                "issues": ["Image file not found."]
            }

        try:
            image = cv2.imread(image_path)

            if image is None:
                return {
                    "readable": False,
                    "quality_score": 0.0,
                    "sharpness_score": 0.0,
                    "brightness_score": 0.0,
                    "resolution_score": 0.0,
                    "non_blank_ratio": 0.0,
                    "issues": ["Image could not be decoded."]
                }

            height, width = image.shape[:2]

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # --------------------------------------------------
            # 1. RESOLUTION
            # --------------------------------------------------
            resolution_score = DocumentQualityEngine._resolution_score(
                width,
                height
            )

            # --------------------------------------------------
            # 2. SHARPNESS / BLUR
            # --------------------------------------------------
            laplacian_variance = float(
                cv2.Laplacian(gray, cv2.CV_64F).var()
            )

            sharpness_score = DocumentQualityEngine._sharpness_score(
                laplacian_variance
            )

            # --------------------------------------------------
            # 3. BRIGHTNESS / EXPOSURE
            # --------------------------------------------------
            mean_brightness = float(gray.mean())

            brightness_score = DocumentQualityEngine._brightness_score(
                mean_brightness
            )

            # --------------------------------------------------
            # 4. BLANK / NEAR-BLANK DETECTION
            # --------------------------------------------------
            # Pixels sufficiently different from white.
            non_blank_pixels = cv2.countNonZero(
                cv2.threshold(
                    gray,
                    245,
                    255,
                    cv2.THRESH_BINARY_INV
                )[1]
            )

            total_pixels = gray.shape[0] * gray.shape[1]

            non_blank_ratio = (
                non_blank_pixels / total_pixels
                if total_pixels > 0
                else 0.0
            )

            # --------------------------------------------------
            # 5. COLLECT QUALITY ISSUES
            # --------------------------------------------------
            issues: List[str] = []

            if width < DocumentQualityEngine.MIN_WIDTH:
                issues.append(
                    f"Image width is too low ({width}px)."
                )

            if height < DocumentQualityEngine.MIN_HEIGHT:
                issues.append(
                    f"Image height is too low ({height}px)."
                )

            if laplacian_variance < DocumentQualityEngine.VERY_BLURRY:
                issues.append(
                    "Image is severely blurred or out of focus."
                )
            elif laplacian_variance < DocumentQualityEngine.LOW_SHARPNESS:
                issues.append(
                    "Image sharpness is low. Text may be difficult to read."
                )

            if mean_brightness < DocumentQualityEngine.MIN_BRIGHTNESS:
                issues.append(
                    "Image is too dark."
                )

            if mean_brightness > DocumentQualityEngine.MAX_BRIGHTNESS:
                issues.append(
                    "Image is overexposed."
                )

            if non_blank_ratio < DocumentQualityEngine.MIN_NON_BLANK_RATIO:
                issues.append(
                    "Image appears blank or contains very little visible content."
                )

            # --------------------------------------------------
            # 6. OVERALL QUALITY SCORE
            # --------------------------------------------------
            quality_score = round(
                (
                    resolution_score * 0.25
                    + sharpness_score * 0.45
                    + brightness_score * 0.20
                    + min(100.0, non_blank_ratio * 500.0) * 0.10
                ),
                1
            )
            # Hard rejection conditions.
            # Exposure warnings alone should not reject a document.
            # Blur, insufficient resolution, or near-blank content are hard failures.
            readable = (
                width >= DocumentQualityEngine.MIN_WIDTH
                and height >= DocumentQualityEngine.MIN_HEIGHT
                and laplacian_variance >= DocumentQualityEngine.VERY_BLURRY
                and non_blank_ratio >= DocumentQualityEngine.MIN_NON_BLANK_RATIO
            )

            return {
                "readable": readable,
                "quality_score": quality_score,
                "sharpness_score": round(sharpness_score, 1),
                "brightness_score": round(brightness_score, 1),
                "resolution_score": round(resolution_score, 1),
                "laplacian_variance": round(laplacian_variance, 2),
                "mean_brightness": round(mean_brightness, 2),
                "width": width,
                "height": height,
                "non_blank_ratio": round(non_blank_ratio, 4),
                "issues": issues
            }

        except Exception as exc:
            logger.exception(
                "Document quality inspection failed: %s",
                exc
            )

            return {
                "readable": False,
                "quality_score": 0.0,
                "sharpness_score": 0.0,
                "brightness_score": 0.0,
                "resolution_score": 0.0,
                "non_blank_ratio": 0.0,
                "issues": [
                    f"Image quality inspection failed: {str(exc)}"
                ]
            }

    @staticmethod
    def _resolution_score(width: int, height: int) -> float:
        """
        Score image resolution from 0-100.
        """

        min_dimension = min(width, height)

        if min_dimension < 400:
            return 0.0

        if min_dimension < 700:
            return 40.0

        if min_dimension < 1000:
            return 70.0

        if min_dimension < 1500:
            return 85.0

        return 100.0

    @staticmethod
    def _sharpness_score(laplacian_variance: float) -> float:
        """
        Convert Laplacian variance into a 0-100 sharpness score.
        """

        if laplacian_variance < 20:
            return 0.0

        if laplacian_variance < 40:
            return 25.0

        if laplacian_variance < 80:
            return 50.0

        if laplacian_variance < 150:
            return 70.0

        if laplacian_variance < 300:
            return 85.0

        return 100.0

    @staticmethod
    def _brightness_score(mean_brightness: float) -> float:
        """
        Score reasonable exposure.
        """

        if mean_brightness < 20:
            return 0.0

        if mean_brightness < 35:
            return 40.0

        if mean_brightness > 245:
            return 20.0

        if mean_brightness > 225:
            return 50.0

        return 100.0


document_quality_engine = DocumentQualityEngine()