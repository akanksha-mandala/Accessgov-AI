import pytest
from services.simplifier import simplifier_service
from services.translation_service import translation_service


def test_terminology_simplifier():
    """
    Unit test for government terminology simplification service.
    """
    res = simplifier_service.simplify_term("Domicile Certificate")
    assert res.original_term == "Domicile Certificate"
    assert "permanently live" in res.simple_explanation.lower()
    assert len(res.key_points) > 0


def test_translation_interface():
    """
    Unit test for multi-lingual translation interface placeholder.
    """
    translated_ta = translation_service.translate_text("eligible", target_lang="ta")
    assert "தகுதியானவர்" in translated_ta or "[TA]" in translated_ta

    translated_hi = translation_service.translate_text("eligible", target_lang="hi")
    assert "पात्र" in translated_hi or "[HI]" in translated_hi
