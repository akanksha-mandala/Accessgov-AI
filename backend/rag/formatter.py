from typing import List, Dict, Any


class ContextFormatter:
    """
    RAG Context Formatter (Refinement #2).
    Formats raw retrieved vector chunks from ChromaDB into structured text blocks for LLM prompts.
    """

    @staticmethod
    def format_retrieved_context(
        chunks: List[Dict[str, Any]],
        header: str = "OFFICIAL GOVERNMENT SCHEME KNOWLEDGE CONTEXT"
    ) -> str:
        """
        Formats a list of retrieved ChromaDB chunks into a clean, markdown-formatted context section.
        """
        if not chunks:
            return f"### {header}\nNo relevant government scheme documentation was found for this query."

        formatted_blocks = [f"### {header}\n"]
        for idx, chunk in enumerate(chunks, 1):
            text = chunk.get("chunk_text", "").strip()
            meta = chunk.get("metadata", {})
            title = meta.get("title", meta.get("service_code", f"Document {idx}"))
            dept = meta.get("department", "Government Department")
            score = chunk.get("score", 0.0)

            block = (
                f"--- ITEM {idx}: {title} ---\n"
                f"Department: {dept}\n"
                f"Relevance Score: {score:.2f}\n"
                f"Content:\n{text}\n"
            )
            formatted_blocks.append(block)

        return "\n".join(formatted_blocks)


context_formatter = ContextFormatter()
