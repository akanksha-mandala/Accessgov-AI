import json
import logging
import os
from typing import Any, Dict, List, Tuple

from schemas.document import OCRResult
from config import settings
from document_intelligence.quality_engine import document_quality_engine

logger = logging.getLogger("accessgov.document_intelligence.ocr_engine")


class OCREngine:
    """
    Real OCR engine for AccessGov AI.

    Pipeline:
        Document quality inspection
        -> PaddleOCR text detection
        -> PaddleOCR text recognition
        -> Actual OCR confidence
        -> OCR result

    Notes:
        - readability_score comes from the physical document-quality engine.
        - OCR confidence comes from PaddleOCR recognition scores.
        - No OCR confidence is fabricated.
        - Government verification is NOT performed here.
    """

    def __init__(self, lang: str = None):
        self.lang = lang or settings.OCR_LANGUAGE
        self._paddle = None

        # Initialize PaddleOCR during backend startup rather than
        # making the first document upload wait for model loading.
        self._initialize_paddle_ocr()

    # ============================================================
    # PADDLE OCR INITIALIZATION
    # ============================================================

    def _initialize_paddle_ocr(self) -> None:
        """
        Initialize the lightweight PaddleOCR pipeline.

        We keep:
            - text detection
            - text recognition

        We disable:
            - document orientation classification
            - document unwarping
            - text-line orientation classification

        Those additional stages are not required for the normal
        document OCR workflow and can make CPU inference extremely
        slow on Windows.
        """

        if self._paddle is not None:
            return

        try:
            from paddleocr import PaddleOCR

            logger.info(
                "Initializing PaddleOCR instance with language: '%s'",
                self.lang,
            )

            self._paddle = PaddleOCR(
                text_detection_model_name="PP-OCRv5_mobile_det",
                text_recognition_model_name="en_PP-OCRv5_mobile_rec",
                use_doc_orientation_classify=False,
                use_doc_unwarping=False,
                use_textline_orientation=False,
            )

            logger.info(
                "PaddleOCR initialized successfully."
            )

        except Exception as exc:
            self._paddle = None

            logger.error(
                "PaddleOCR initialization failed: %s",
                exc,
                exc_info=True,
            )

    def _get_paddle_ocr(self):
        """
        Return the initialized PaddleOCR instance.

        If startup initialization failed, retry initialization when
        OCR is requested.
        """

        if self._paddle is None:
            self._initialize_paddle_ocr()

        return self._paddle

    # ============================================================
    # PADDLE RESULT NORMALIZATION
    # ============================================================

    @staticmethod
    def _normalize_paddle_result(
        result: Any,
    ) -> Dict[str, Any]:
        """
        Normalize PaddleOCR 3.x OCRResult into a dictionary.

        PaddleOCR 3.x can return OCRResult objects whose actual
        result is exposed through .json() or .res.
        """

        # --------------------------------------------------------
        # Preferred PaddleOCR 3.x representation
        # --------------------------------------------------------

        try:
            result_json = getattr(
                result,
                "json",
                None,
            )

            if callable(result_json):
                result_json = result_json()

            if isinstance(result_json, str):
                result_json = json.loads(
                    result_json
                )

            if isinstance(result_json, dict):
                return result_json

        except Exception as exc:
            logger.debug(
                "Unable to normalize PaddleOCR result via .json(): %s",
                exc,
            )

        # --------------------------------------------------------
        # .res representation
        # --------------------------------------------------------

        try:
            result_res = getattr(
                result,
                "res",
                None,
            )

            if isinstance(result_res, dict):
                return result_res

        except Exception as exc:
            logger.debug(
                "Unable to normalize PaddleOCR result via .res: %s",
                exc,
            )

        # --------------------------------------------------------
        # Dictionary result
        # --------------------------------------------------------

        if isinstance(result, dict):
            return result

        # --------------------------------------------------------
        # Dictionary-like compatibility
        # --------------------------------------------------------

        try:
            converted = dict(result)

            if isinstance(converted, dict):
                return converted

        except Exception:
            pass

        return {}

    # ============================================================
    # EXTRACT OCR DATA
    # ============================================================

    def _extract_paddle_result(
        self,
        result: Any,
    ) -> Tuple[
        List[str],
        List[float],
        List[Any],
        List[Dict[str, Any]],
    ]:
        """
        Extract recognized text, actual recognition confidence,
        and bounding boxes from one PaddleOCR result.
        """

        data = self._normalize_paddle_result(
            result
        )

        # PaddleOCR 3.x commonly exposes these fields directly.
        rec_texts = data.get(
            "rec_texts",
            [],
        ) or []

        rec_scores = data.get(
            "rec_scores",
            [],
        ) or []

        rec_polys = data.get(
            "rec_polys",
            [],
        ) or []

        rec_boxes = data.get(
            "rec_boxes",
            [],
        ) or []

        # Compatibility with nested "res" structures.
        if (
            not rec_texts
            and isinstance(
                data.get("res"),
                dict,
            )
        ):
            nested = data["res"]

            rec_texts = nested.get(
                "rec_texts",
                [],
            ) or []

            rec_scores = nested.get(
                "rec_scores",
                [],
            ) or []

            rec_polys = nested.get(
                "rec_polys",
                [],
            ) or []

            rec_boxes = nested.get(
                "rec_boxes",
                [],
            ) or []

        extracted_texts: List[str] = []
        confidence_scores: List[float] = []
        boxes: List[Any] = []
        normalized_regions: List[
            Dict[str, Any]
        ] = []

        for index, raw_text in enumerate(
            rec_texts
        ):
            if raw_text is None:
                continue

            text = str(
                raw_text
            ).strip()

            if not text:
                continue

            # ----------------------------------------------------
            # Actual PaddleOCR confidence
            # ----------------------------------------------------

            confidence = 0.0

            if index < len(rec_scores):
                try:
                    confidence = float(
                        rec_scores[index]
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    confidence = 0.0

            confidence = max(
                0.0,
                min(
                    1.0,
                    confidence,
                ),
            )

            # ----------------------------------------------------
            # Bounding box
            # ----------------------------------------------------

            bbox = []

            if index < len(rec_polys):
                bbox = rec_polys[index]

            elif index < len(rec_boxes):
                bbox = rec_boxes[index]

            try:
                if hasattr(
                    bbox,
                    "tolist",
                ):
                    bbox = bbox.tolist()
            except Exception:
                pass

            extracted_texts.append(
                text
            )

            confidence_scores.append(
                confidence
            )

            boxes.append(
                bbox
            )

            normalized_regions.append(
                {
                    "box": bbox,
                    "text": text,
                    "conf": confidence,
                }
            )

        return (
            extracted_texts,
            confidence_scores,
            boxes,
            normalized_regions,
        )

    # ============================================================
    # MAIN DOCUMENT PROCESSOR
    # ============================================================

    def process_document(
        self,
        file_path: str,
        mime_type: str = "image/jpeg",
    ) -> OCRResult:
        """
        Process either an image or PDF.
        """

        if (
            not file_path
            or not os.path.exists(file_path)
        ):
            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=0,
                bounding_boxes=[],
                readability_score=0.0,
                quality_issues=[
                    "Document file not found."
                ],
                sharpness_score=0.0,
                error_message=(
                    "Document file not found "
                    "on storage disk."
                ),
            )

        if (
            file_path.lower().endswith(".pdf")
            or "pdf" in mime_type.lower()
        ):
            return self._process_pdf(
                file_path
            )

        return self._process_image(
            file_path
        )

    # ============================================================
    # IMAGE OCR
    # ============================================================

    def _process_image(
        self,
        image_path: str,
    ) -> OCRResult:
        """
        Inspect physical image quality and then perform genuine
        PaddleOCR detection + recognition.
        """

        # --------------------------------------------------------
        # 1. DOCUMENT QUALITY
        # --------------------------------------------------------

        quality = (
            document_quality_engine.inspect_image(
                image_path
            )
        )

        quality_issues = quality.get(
            "issues",
            [],
        )

        readability_score = float(
            quality.get(
                "quality_score",
                0.0,
            )
        )

        sharpness_score = float(
            quality.get(
                "sharpness_score",
                0.0,
            )
        )

        # --------------------------------------------------------
        # 2. PHYSICAL READABILITY FAILURE
        # --------------------------------------------------------

        if not quality.get(
            "readable",
            False,
        ):
            issue_text = "; ".join(
                quality_issues
            )

            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=1,
                bounding_boxes=[],
                readability_score=readability_score,
                quality_issues=quality_issues,
                sharpness_score=sharpness_score,
                error_message=(
                    "The uploaded document is not "
                    "sufficiently readable. "
                    f"{issue_text} "
                    "Please upload a clear, well-lit, "
                    "focused document image."
                ),
            )

        # --------------------------------------------------------
        # 3. GET PADDLE OCR
        # --------------------------------------------------------

        paddle = self._get_paddle_ocr()

        if paddle is None:
            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=1,
                bounding_boxes=[],
                readability_score=readability_score,
                quality_issues=quality_issues,
                sharpness_score=sharpness_score,
                error_message=(
                    "PaddleOCR could not be initialized."
                ),
            )

        extracted_text_lines: List[str] = []
        confidence_scores: List[float] = []
        bounding_boxes: List[
            Dict[str, Any]
        ] = []

        # --------------------------------------------------------
        # 4. ACTUAL OCR INFERENCE
        # --------------------------------------------------------

        try:
            logger.info(
                "Running PaddleOCR on image: %s",
                image_path,
            )

            results = paddle.predict(
                image_path
            )

            if results:

                for result in results:

                    (
                        page_texts,
                        page_confidences,
                        _,
                        page_regions,
                    ) = self._extract_paddle_result(
                        result
                    )

                    extracted_text_lines.extend(
                        page_texts
                    )

                    confidence_scores.extend(
                        page_confidences
                    )

                    bounding_boxes.extend(
                        page_regions
                    )

            logger.info(
                "PaddleOCR extracted %d text regions from %s.",
                len(
                    extracted_text_lines
                ),
                image_path,
            )

        except Exception as exc:
            logger.error(
                "PaddleOCR image execution failed: %s",
                exc,
                exc_info=True,
            )

            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=1,
                bounding_boxes=[],
                readability_score=readability_score,
                quality_issues=quality_issues,
                sharpness_score=sharpness_score,
                error_message=(
                    "OCR processing failed while "
                    "analyzing the document."
                ),
            )

        # --------------------------------------------------------
        # 5. NO TEXT DETECTED
        # --------------------------------------------------------

        if not extracted_text_lines:

            logger.warning(
                "OCR returned no readable text for image: %s",
                image_path,
            )

            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=1,
                bounding_boxes=[],
                readability_score=readability_score,
                quality_issues=quality_issues,
                sharpness_score=sharpness_score,
                error_message=(
                    "The document image appears readable "
                    "visually, but OCR could not extract "
                    "usable text."
                ),
            )

        # --------------------------------------------------------
        # 6. ACTUAL OCR CONFIDENCE
        # --------------------------------------------------------

        full_text = "\n".join(
            extracted_text_lines
        )

        avg_confidence = (
            sum(confidence_scores)
            / len(confidence_scores)
            if confidence_scores
            else 0.0
        )

        avg_confidence = round(
            max(
                0.0,
                min(
                    1.0,
                    avg_confidence,
                ),
            ),
            4,
        )

        logger.info(
            "Actual OCR confidence for %s: %.4f",
            image_path,
            avg_confidence,
        )

        # --------------------------------------------------------
        # 7. SUCCESS
        # --------------------------------------------------------

        return OCRResult(
            status="success",
            raw_text=full_text,
            confidence=avg_confidence,
            page_count=1,
            bounding_boxes=bounding_boxes,
            readability_score=readability_score,
            quality_issues=quality_issues,
            sharpness_score=sharpness_score,
        )

    # ============================================================
    # PDF OCR
    # ============================================================

    def _process_pdf(
        self,
        pdf_path: str,
    ) -> OCRResult:
        """
        Process searchable PDFs directly.

        For scanned PDFs:
            PDF -> rendered page image -> quality inspection
            -> PaddleOCR -> combined result.
        """

        # --------------------------------------------------------
        # 1. TRY NATIVE PDF TEXT
        # --------------------------------------------------------

        extracted_pages: List[str] = []

        try:
            import pypdf

            reader = pypdf.PdfReader(
                pdf_path
            )

            for page in reader.pages:

                text = page.extract_text()

                if text and text.strip():
                    extracted_pages.append(
                        text.strip()
                    )

        except Exception as exc:
            logger.warning(
                "PyPDF extraction error: %s",
                exc,
            )

        # --------------------------------------------------------
        # 2. SEARCHABLE PDF
        # --------------------------------------------------------

        if extracted_pages:

            full_text = "\n\n".join(
                extracted_pages
            )

            return OCRResult(
                status="success",
                raw_text=full_text,
                confidence=0.0,
                page_count=len(
                    extracted_pages
                ),
                bounding_boxes=[],
                readability_score=100.0,
                quality_issues=[
                    (
                        "Text extracted directly from "
                        "searchable PDF; OCR confidence "
                        "is not applicable."
                    )
                ],
                sharpness_score=100.0,
            )

        # --------------------------------------------------------
        # 3. SCANNED PDF -> IMAGES
        # --------------------------------------------------------

        try:
            from pdf2image import (
                convert_from_path,
            )

            poppler_path = (
                r"C:\Users\HP\Downloads\Release-26.09.0-0"
                r"\poppler-26.09.0\Library\bin"
            )

            logger.info(
                "Rendering scanned PDF for OCR: %s",
                pdf_path,
            )

            images = convert_from_path(
                pdf_path,
                dpi=120,
                poppler_path=poppler_path,
            )

            if not images:

                return OCRResult(
                    status="ocr_failed",
                    raw_text="",
                    confidence=0.0,
                    page_count=0,
                    bounding_boxes=[],
                    readability_score=0.0,
                    quality_issues=[
                        (
                            "No pages could be "
                            "rendered from the PDF."
                        )
                    ],
                    sharpness_score=0.0,
                    error_message=(
                        "The PDF could not be rendered "
                        "into images."
                    ),
                )

            logger.info(
                "Rendered %d PDF page(s) for OCR: %s",
                len(images),
                pdf_path,
            )

            page_quality_scores: List[
                float
            ] = []

            page_sharpness_scores: List[
                float
            ] = []

            page_issues: List[str] = []

            successful_pages: List[
                OCRResult
            ] = []

            # ----------------------------------------------------
            # 4. OCR EVERY PAGE
            # ----------------------------------------------------

            for idx, img in enumerate(
                images
            ):

                temp_img_path = (
                    f"{pdf_path}_page_{idx}.png"
                )

                try:

                    img.save(
                        temp_img_path,
                        "PNG",
                    )

                    logger.info(
                        "Processing PDF page %d/%d with OCR.",
                        idx + 1,
                        len(images),
                    )

                    # Physical quality.
                    quality = (
                        document_quality_engine.inspect_image(
                            temp_img_path
                        )
                    )

                    page_quality_scores.append(
                        float(
                            quality.get(
                                "quality_score",
                                0.0,
                            )
                        )
                    )

                    page_sharpness_scores.append(
                        float(
                            quality.get(
                                "sharpness_score",
                                0.0,
                            )
                        )
                    )

                    page_issues.extend(
                        quality.get(
                            "issues",
                            [],
                        )
                    )

                    # Genuine OCR.
                    page_result = (
                        self._process_image(
                            temp_img_path
                        )
                    )

                    if (
                        page_result.status
                        == "success"
                        and page_result.raw_text.strip()
                    ):
                        successful_pages.append(
                            page_result
                        )

                finally:

                    if os.path.exists(
                        temp_img_path
                    ):

                        try:
                            os.remove(
                                temp_img_path
                            )

                        except Exception as cleanup_error:

                            logger.warning(
                                "Failed to delete temporary "
                                "OCR image %s: %s",
                                temp_img_path,
                                cleanup_error,
                            )

            # ----------------------------------------------------
            # 5. ALL PAGES FAILED OCR
            # ----------------------------------------------------

            if not successful_pages:

                avg_quality = (
                    sum(
                        page_quality_scores
                    )
                    / len(
                        page_quality_scores
                    )
                    if page_quality_scores
                    else 0.0
                )

                avg_sharpness = (
                    sum(
                        page_sharpness_scores
                    )
                    / len(
                        page_sharpness_scores
                    )
                    if page_sharpness_scores
                    else 0.0
                )

                unique_issues = list(
                    dict.fromkeys(
                        page_issues
                    )
                )

                return OCRResult(
                    status="ocr_failed",
                    raw_text="",
                    confidence=0.0,
                    page_count=len(
                        images
                    ),
                    bounding_boxes=[],
                    readability_score=round(
                        avg_quality,
                        1,
                    ),
                    quality_issues=unique_issues,
                    sharpness_score=round(
                        avg_sharpness,
                        1,
                    ),
                    error_message=(
                        "The scanned PDF was rendered "
                        "successfully, but OCR could not "
                        "extract usable text."
                    ),
                )

            # ----------------------------------------------------
            # 6. COMBINE OCR RESULTS
            # ----------------------------------------------------

            full_text = "\n\n".join(
                page.raw_text
                for page in successful_pages
            )

            # ----------------------------------------------------
            # ACTUAL OCR CONFIDENCE
            # ----------------------------------------------------

            page_confidences = [
                page.confidence
                for page in successful_pages
                if page.confidence > 0
            ]

            actual_confidence = (
                sum(page_confidences)
                / len(page_confidences)
                if page_confidences
                else 0.0
            )

            # ----------------------------------------------------
            # PHYSICAL QUALITY
            # ----------------------------------------------------

            avg_quality = (
                sum(
                    page_quality_scores
                )
                / len(
                    page_quality_scores
                )
                if page_quality_scores
                else 0.0
            )

            avg_sharpness = (
                sum(
                    page_sharpness_scores
                )
                / len(
                    page_sharpness_scores
                )
                if page_sharpness_scores
                else 0.0
            )

            unique_issues = list(
                dict.fromkeys(
                    page_issues
                )
            )

            # ----------------------------------------------------
            # COMBINE BOUNDING BOXES
            # ----------------------------------------------------

            combined_boxes: List[
                Dict[str, Any]
            ] = []

            for page_number, page in enumerate(
                successful_pages,
                start=1,
            ):

                for box in page.bounding_boxes:

                    combined_box = dict(
                        box
                    )

                    combined_box[
                        "page"
                    ] = page_number

                    combined_boxes.append(
                        combined_box
                    )

            # ----------------------------------------------------
            # SUCCESS
            # ----------------------------------------------------

            return OCRResult(
                status="success",
                raw_text=full_text,
                confidence=round(
                    actual_confidence,
                    4,
                ),
                page_count=len(
                    images
                ),
                bounding_boxes=combined_boxes,
                readability_score=round(
                    avg_quality,
                    1,
                ),
                quality_issues=unique_issues,
                sharpness_score=round(
                    avg_sharpness,
                    1,
                ),
            )

        # --------------------------------------------------------
        # 7. PDF PROCESSING ERROR
        # --------------------------------------------------------

        except Exception as exc:

            logger.error(
                "PDF OCR processing failed: %s",
                exc,
                exc_info=True,
            )

            return OCRResult(
                status="ocr_failed",
                raw_text="",
                confidence=0.0,
                page_count=1,
                bounding_boxes=[],
                readability_score=0.0,
                quality_issues=[
                    "Unable to render scanned PDF pages."
                ],
                sharpness_score=0.0,
                error_message=(
                    "The PDF could not be processed. "
                    "Please upload a searchable PDF "
                    "or clear document image."
                ),
            )


# ================================================================
# GLOBAL OCR ENGINE
# ================================================================

ocr_engine = OCREngine()