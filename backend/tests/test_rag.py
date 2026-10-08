import pytest
from rag.embeddings import embedding_manager
from rag.formatter import context_formatter
from rag.prompts import ELIGIBILITY_EXPLANATION_PROMPT


def test_embedding_generation():
    """
    Unit test for SentenceTransformer vector embedding manager.
    """
    vector = embedding_manager.embed_text("Income certificate eligibility criteria")
    assert isinstance(vector, list)
    assert len(vector) > 0


def test_context_formatter():
    """
    Unit test for RAG context formatter.
    """
    chunks = [
        {
            "chunk_text": "Scheme: Income Certificate\nDepartment: Revenue Department",
            "metadata": {"title": "Income Certificate", "department": "Revenue Department"},
            "score": 0.92
        }
    ]
    formatted = context_formatter.format_retrieved_context(chunks)
    assert "OFFICIAL GOVERNMENT SCHEME KNOWLEDGE CONTEXT" in formatted
    assert "Income Certificate" in formatted
    assert "0.92" in formatted


def test_prompt_template_formatting():
    """
    Unit test for centralized prompt template string formatting.
    """
    prompt = ELIGIBILITY_EXPLANATION_PROMPT.format(
        context="Sample scheme details",
        citizen_profile="Income ₹1,20,000 per annum"
    )
    assert "AccessGov AI" in prompt
    assert "Sample scheme details" in prompt
