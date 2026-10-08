import logging
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from schemas.agent import ToolExecutionResult
from schemas.eligibility import EligibilityCheckRequest
from services.service_catalog import service_catalog_service
from services.eligibility_engine import eligibility_engine
from services.simplifier import simplifier_service
from services.translation_service import translation_service
from services.document_service import document_service
import crud.crud_document as crud_document
from rag.retriever import knowledge_retriever
from rag.formatter import context_formatter

logger = logging.getLogger("accessgov.agents.tools")


class ADKTools:
    """
    Google ADK Tool Wrappers.
    Bridges agent execution to existing Module 3 & Module 5 backend services without duplicating business logic.
    Every tool returns a standardized JSON `ToolExecutionResult` containing data, sources, and execution status.
    """

    @staticmethod
    def discover_service_tool(
        db: Session,
        query: str,
        category: Optional[str] = None,
        district: Optional[str] = None,
        limit: int = 5
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Invokes `service_catalog_service.hybrid_search_services`.
        """
        try:
            results = service_catalog_service.hybrid_search_services(
                db=db,
                query=query,
                category=category,
                district=district,
                limit=limit
            )
            data_items = []
            sources = []
            for item in results:
                s = item["service"]
                data_items.append({
                    "service_id": s.id,
                    "title": s.title,
                    "code": s.code,
                    "category": s.category,
                    "department": s.department,
                    "description": s.description,
                    "relevance_score": item["score"],
                    "processing_days": s.processing_days,
                    "fee": s.fee_amount
                })
                sources.append({
                    "service_code": s.code,
                    "service_title": s.title,
                    "match_type": item["match_type"]
                })

            return ToolExecutionResult(
                tool_name="discover_service_tool",
                success=True,
                data=data_items,
                sources=sources,
                confidence=0.90 if data_items else 0.50,
                execution_message=f"Found {len(data_items)} matching services."
            )
        except Exception as e:
            logger.error(f"discover_service_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="discover_service_tool",
                success=False,
                data=[],
                execution_message=f"Error discovering services: {str(e)}"
            )

    @staticmethod
    def eligibility_tool(
        db: Session,
        request: EligibilityCheckRequest
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Invokes `eligibility_engine.evaluate_eligibility`.
        """
        try:
            result = eligibility_engine.evaluate_eligibility(db, request)
            return ToolExecutionResult(
                tool_name="eligibility_tool",
                success=True,
                data=result.model_dump(),
                sources=[{"service_id": request.service_id, "service_code": request.service_code}],
                confidence=0.95,
                execution_message=f"Evaluated status: {result.eligibility_status} with readiness score {result.readiness_score}%."
            )
        except Exception as e:
            logger.error(f"eligibility_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="eligibility_tool",
                success=False,
                data=None,
                execution_message=f"Error evaluating eligibility: {str(e)}"
            )

    @staticmethod
    def requirements_tool(
        db: Session,
        service_id: int
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Queries document requirements using `crud_requirement`.
        """
        try:
            import crud.crud_requirement as crud_requirement
            import crud.crud_service as crud_service
            service = crud_service.get_service_by_id(db, service_id)
            reqs = crud_requirement.get_service_requirements(db, service_id)
            doc_names = [r.document_name for r in reqs] if reqs else [
                "Aadhaar Card", "Ration Card", "Income Certificate", "Passport Photograph"
            ]
            
            service_title = service.title if service else f"Service ID {service_id}"
            return ToolExecutionResult(
                tool_name="requirements_tool",
                success=True,
                data={
                    "service_id": service_id,
                    "service_title": service_title,
                    "required_documents": doc_names
                },
                sources=[{"service_id": service_id, "service_title": service_title}],
                confidence=0.95,
                execution_message=f"Retrieved {len(doc_names)} document requirements."
            )
        except Exception as e:
            logger.error(f"requirements_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="requirements_tool",
                success=False,
                data=None,
                execution_message=f"Error retrieving requirements: {str(e)}"
            )

    @staticmethod
    def simplifier_tool(
        term: str,
        language: str = "en"
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Invokes `simplifier_service.simplify_term`.
        """
        try:
            explanation = simplifier_service.simplify_term(term, language=language)
            return ToolExecutionResult(
                tool_name="simplifier_tool",
                success=True,
                data=explanation.model_dump(),
                confidence=0.90,
                execution_message=f"Simplified term '{term}'."
            )
        except Exception as e:
            logger.error(f"simplifier_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="simplifier_tool",
                success=False,
                data=None,
                execution_message=f"Error simplifying term: {str(e)}"
            )

    @staticmethod
    def translation_tool(
        text: str,
        target_lang: str = "en"
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Invokes `translation_service.translate_text`.
        """
        try:
            translated = translation_service.translate_text(text, target_lang=target_lang)
            return ToolExecutionResult(
                tool_name="translation_tool",
                success=True,
                data={"translated_text": translated, "target_language": target_lang},
                confidence=0.85,
                execution_message=f"Translated text to '{target_lang}'."
            )
        except Exception as e:
            logger.error(f"translation_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="translation_tool",
                success=False,
                data={"translated_text": text, "target_language": target_lang},
                execution_message=f"Error translating text: {str(e)}"
            )

    @staticmethod
    def rag_retrieval_tool(
        query: str,
        top_k: int = 4
    ) -> ToolExecutionResult:
        """
        Tool Wrapper: Invokes `knowledge_retriever.retrieve_chunks` and `context_formatter.format_retrieved_context`.
        """
        try:
            chunks = knowledge_retriever.retrieve_chunks(query=query, top_k=top_k)
            formatted_context = context_formatter.format_retrieved_context(chunks)
            sources = [c.get("metadata", {}) for c in chunks]

            return ToolExecutionResult(
                tool_name="rag_retrieval_tool",
                success=True,
                data={"formatted_context": formatted_context, "chunk_count": len(chunks)},
                sources=sources,
                confidence=0.90 if chunks else 0.50,
                execution_message=f"Retrieved {len(chunks)} knowledge chunks from RAG vector store."
            )
        except Exception as e:
            logger.error(f"rag_retrieval_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="rag_retrieval_tool",
                success=False,
                data={"formatted_context": "No RAG context available.", "chunk_count": 0},
                execution_message=f"Error retrieving RAG context: {str(e)}"
            )

    @staticmethod
    def document_analysis_tool(
        db: Session,
        document_id: int,
        user_id: int
    ) -> ToolExecutionResult:
        """
        Session 5 Tool Wrapper (Refinement #10): Invokes `document_service.analyze_document_file` for an existing uploaded document.
        Reuses backend services without duplicating OCR/classification/validation logic inside agent code.
        """
        try:
            doc = crud_document.get_document_by_id(db, document_id)
            if not doc:
                return ToolExecutionResult(
                    tool_name="document_analysis_tool",
                    success=False,
                    data=None,
                    execution_message=f"Document with ID {document_id} not found."
                )

            # Check ownership security
            if doc.user_id != user_id:
                return ToolExecutionResult(
                    tool_name="document_analysis_tool",
                    success=False,
                    data=None,
                    execution_message="Access denied: User does not own this document."
                )

            res = document_service.analyze_document_file(
                db=db,
                user_id=user_id,
                file_path=doc.file_path,
                original_file_name=doc.file_name,
                mime_type=doc.mime_type,
                file_size_bytes=doc.file_size_bytes
            )

            return ToolExecutionResult(
                tool_name="document_analysis_tool",
                success=True,
                data=res.model_dump(),
                sources=[{"document_id": document_id, "document_type": res.document_type}],
                confidence=res.classification_confidence,
                execution_message=f"Analyzed document {document_id} ({res.document_type}). Readiness score: {res.readiness_result.readiness_score}%."
            )
        except Exception as e:
            logger.error(f"document_analysis_tool failed: {str(e)}")
            return ToolExecutionResult(
                tool_name="document_analysis_tool",
                success=False,
                data=None,
                execution_message=f"Error analyzing document: {str(e)}"
            )


adk_tools = ADKTools()
