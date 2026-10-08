import os
import pytest
from fastapi import HTTPException
from utils.file_storage import file_storage_util
from agents.tools import adk_tools


def test_unsupported_file_extension():
    """
    Test uploading unsupported file extension raises HTTP 400 Bad Request.
    """
    class MockFile:
        filename = "script.exe"
        content_type = "application/x-msdownload"
        file = None

    with pytest.raises(HTTPException) as exc_info:
        file_storage_util.validate_and_save_upload(MockFile())
    assert exc_info.value.status_code == 400
    assert "Unsupported file format" in exc_info.value.detail


def test_document_analysis_tool_non_existent():
    """
    Test ADK tool wrapper handling non-existent document ID.
    """
    res = adk_tools.document_analysis_tool(db=None, document_id=99999, user_id=1)
    assert res.success is False
    assert "not found" in res.execution_message.lower()
