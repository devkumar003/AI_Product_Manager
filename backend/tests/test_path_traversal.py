"""
Regression tests for path traversal prevention (ISSUE 3)
and input validation constraints (ISSUE 8).
"""
import pytest
from fastapi import HTTPException

from app.services.development.pipelines import safe_filename


class TestSafeFilename:
    """Test safe_filename rejects path traversal and unsafe names."""

    def test_valid_simple_name(self):
        assert safe_filename("MyProject") == "MyProject"

    def test_valid_name_with_spaces(self):
        assert safe_filename("AI ProductOS Billing") == "AI_ProductOS_Billing"

    def test_valid_name_with_dots(self):
        assert safe_filename("v1.2.3") == "v1.2.3"

    def test_valid_name_with_hyphens(self):
        assert safe_filename("my-project") == "my-project"

    def test_valid_name_with_underscores(self):
        assert safe_filename("my_project") == "my_project"

    def test_empty_string_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("")
        assert exc_info.value.status_code == 400

    def test_whitespace_only_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("   ")
        assert exc_info.value.status_code == 400

    def test_traversal_dotdot_slash(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("../../etc/passwd")
        assert exc_info.value.status_code == 400

    def test_traversal_backslash(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("..\\..\\windows\\system32")
        assert exc_info.value.status_code == 400

    def test_url_encoded_traversal(self):
        """Percent-encoded ../.. should be decoded and rejected."""
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("..%2F..%2Fetc%2Fpasswd")
        assert exc_info.value.status_code == 400

    def test_slash_character_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("path/to/file")
        assert exc_info.value.status_code == 400

    def test_null_byte_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("file\x00.txt")
        assert exc_info.value.status_code == 400

    def test_reserved_name_CON(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("CON")
        assert exc_info.value.status_code == 400

    def test_reserved_name_NUL(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("NUL")
        assert exc_info.value.status_code == 400

    def test_reserved_name_COM1(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("COM1")
        assert exc_info.value.status_code == 400

    def test_reserved_name_case_insensitive(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("con")
        assert exc_info.value.status_code == 400

    def test_reserved_name_with_extension(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("CON.txt")
        assert exc_info.value.status_code == 400

    def test_special_chars_angle_brackets(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("file<script>")
        assert exc_info.value.status_code == 400

    def test_pipe_character_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("file|name")
        assert exc_info.value.status_code == 400

    def test_semicolon_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("file;rm -rf")
        assert exc_info.value.status_code == 400

    def test_unicode_characters_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("файл")
        assert exc_info.value.status_code == 400

    def test_emoji_rejected(self):
        with pytest.raises(HTTPException) as exc_info:
            safe_filename("project🚀")
        assert exc_info.value.status_code == 400
