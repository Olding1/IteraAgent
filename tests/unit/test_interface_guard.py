"""Unit tests for Interface Guard.

Tests the parameter validation and auto-correction functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from src.core.interface_guard import InterfaceGuard
from src.schemas.tool_schema import ToolValidationResult


@pytest.fixture
def mock_builder_client():
    """Create a mock builder client."""
    client = MagicMock()
    client.call = AsyncMock()
    return client


@pytest.fixture
def sample_schema():
    """Sample tool schema for testing."""
    return {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "max_results": {"type": "integer", "description": "Maximum number of results"},
        },
        "required": ["query"],
    }


class TestInterfaceGuardValidation:
    """Test validation functionality."""

    def test_validate_success(self, mock_builder_client, sample_schema):
        """Test successful validation."""
        guard = InterfaceGuard(mock_builder_client)

        args = {"query": "test search", "max_results": 5}
        is_valid, errors = guard.validate_sync("test_tool", args, sample_schema)

        assert is_valid is True
        assert len(errors) == 0

    def test_validate_missing_required_param(self, mock_builder_client, sample_schema):
        """Test validation fails when required parameter is missing."""
        guard = InterfaceGuard(mock_builder_client)

        args = {"max_results": 5}  # Missing 'query'
        is_valid, errors = guard.validate_sync("test_tool", args, sample_schema)

        assert is_valid is False
        assert len(errors) > 0
        assert any("query" in err.field_name for err in errors)

    def test_validate_wrong_type(self, mock_builder_client, sample_schema):
        """Test validation fails when parameter has wrong type."""
        guard = InterfaceGuard(mock_builder_client)

        args = {"query": "test", "max_results": "not_an_integer"}
        is_valid, errors = guard.validate_sync("test_tool", args, sample_schema)

        assert is_valid is False
        assert len(errors) > 0

    def test_validate_extra_param(self, mock_builder_client, sample_schema):
        """Test validation with extra parameters (should pass)."""
        guard = InterfaceGuard(mock_builder_client)

        args = {"query": "test", "max_results": 5, "extra_field": "value"}
        # Pydantic by default ignores extra fields
        is_valid, errors = guard.validate_sync("test_tool", args, sample_schema)

        # Should still be valid as Pydantic ignores extra fields by default
        assert is_valid is True


class TestInterfaceGuardAutoCorrection:
    """Test auto-correction functionality."""

    @pytest.mark.asyncio
    async def test_auto_correction_success(self, mock_builder_client, sample_schema):
        """Test successful auto-correction."""
        guard = InterfaceGuard(mock_builder_client, max_retries=3)

        # Mock LLM response with corrected parameters
        mock_builder_client.call.return_value = '{"query": "corrected search", "max_results": 10}'

        # Invalid args (missing required field)
        args = {"max_results": 5}

        result = await guard.validate_and_fix("test_tool", args, sample_schema)

        assert result.is_valid is True
        assert result.corrected_args["query"] == "corrected search"
        assert result.retry_count > 0

    @pytest.mark.asyncio
    async def test_auto_correction_max_retries(self, mock_builder_client, sample_schema):
        """Test auto-correction reaches max retries."""
        guard = InterfaceGuard(mock_builder_client, max_retries=2)

        # Mock LLM always returns invalid JSON
        mock_builder_client.call.return_value = '{"invalid": "still missing query"}'

        args = {"max_results": 5}

        result = await guard.validate_and_fix("test_tool", args, sample_schema)

        assert result.is_valid is False
        assert result.retry_count == 2
        assert len(result.errors) > 0

    @pytest.mark.asyncio
    async def test_auto_correction_type_fix(self, mock_builder_client, sample_schema):
        """Test auto-correction fixes type errors."""
        guard = InterfaceGuard(mock_builder_client, max_retries=3)

        # Mock LLM fixes the type error
        mock_builder_client.call.return_value = '{"query": "test", "max_results": 10}'

        # Wrong type for max_results
        args = {"query": "test", "max_results": "not_a_number"}

        result = await guard.validate_and_fix("test_tool", args, sample_schema)

        assert result.is_valid is True
        assert isinstance(result.corrected_args["max_results"], int)


class TestInterfaceGuardEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.asyncio
    async def test_malformed_llm_response(self, mock_builder_client, sample_schema):
        """Test handling of malformed LLM response."""
        guard = InterfaceGuard(mock_builder_client, max_retries=1)

        # Mock LLM returns non-JSON
        mock_builder_client.call.return_value = "This is not JSON"

        args = {"max_results": 5}

        result = await guard.validate_and_fix("test_tool", args, sample_schema)

        # Should fail gracefully
        assert result.is_valid is False

    @pytest.mark.asyncio
    async def test_llm_response_with_json_embedded(self, mock_builder_client, sample_schema):
        """Test extraction of JSON from LLM response with extra text."""
        guard = InterfaceGuard(mock_builder_client, max_retries=1)

        # Mock LLM returns JSON with surrounding text
        mock_builder_client.call.return_value = """
        Here is the corrected JSON:
        {"query": "extracted query", "max_results": 5}
        Hope this helps!
        """

        args = {}

        result = await guard.validate_and_fix("test_tool", args, sample_schema)

        assert result.is_valid is True
        assert result.corrected_args["query"] == "extracted query"

    def test_empty_schema(self, mock_builder_client):
        """Test validation with empty schema."""
        guard = InterfaceGuard(mock_builder_client)

        empty_schema = {"type": "object", "properties": {}}
        args = {}

        is_valid, errors = guard.validate_sync("test_tool", args, empty_schema)

        assert is_valid is True
        assert len(errors) == 0


class TestInterfaceGuardIntegration:
    """Integration tests for Interface Guard."""

    @pytest.mark.asyncio
    async def test_realistic_search_tool_validation(self, mock_builder_client):
        """Test with realistic search tool schema."""
        guard = InterfaceGuard(mock_builder_client)

        search_schema = {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "num_results": {"type": "integer", "description": "Number of results"},
                "language": {"type": "string", "description": "Language code"},
            },
            "required": ["query"],
        }

        # Valid args
        args = {"query": "Agent Zero", "num_results": 10, "language": "zh"}
        is_valid, errors = guard.validate_sync("search_tool", args, search_schema)

        assert is_valid is True

    @pytest.mark.asyncio
    async def test_realistic_calculator_validation(self, mock_builder_client):
        """Test with realistic calculator tool schema."""
        guard = InterfaceGuard(mock_builder_client)

        calc_schema = {
            "type": "object",
            "properties": {"expression": {"type": "string", "description": "Math expression"}},
            "required": ["expression"],
        }

        args = {"expression": "2 + 2"}
        is_valid, errors = guard.validate_sync("calculator", args, calc_schema)

        assert is_valid is True
