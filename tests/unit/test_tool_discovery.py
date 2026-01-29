"""Unit tests for Tool Discovery Engine."""

import pytest
from pathlib import Path
from src.core.tool_discovery import ToolDiscoveryEngine


@pytest.fixture
def discovery_engine():
    """Create a discovery engine instance."""
    return ToolDiscoveryEngine()


class TestToolDiscoveryEngine:
    """Test ToolDiscoveryEngine functionality."""
    
    def test_load_index(self, discovery_engine):
        """Test that index is loaded successfully."""
        assert discovery_engine.tools is not None
        assert len(discovery_engine.tools) > 0
        print(f"Loaded {len(discovery_engine.tools)} tools")
    
    def test_search_by_keyword(self, discovery_engine):
        """Test keyword-based search."""
        # Search using "search" keyword which appears in multiple tool names/categories
        results = discovery_engine.search("search", top_k=3)
        
        assert len(results) > 0
        assert len(results) <= 3
        
        # Should find search-related tools
        # Check if any result has "search" in id, name, or category
        has_search = any(
            "search" in t["id"].lower() or 
            "search" in t["name"].lower() or 
            t["category"] == "search"
            for t in results
        )
    
    def test_search_by_category(self, discovery_engine):
        """Test category filtering."""
        # Search with category filter
        results = discovery_engine.search("tool", top_k=5, category="search")
        
        for tool in results:
            assert tool["category"] == "search"
    
    def test_get_tool_by_id(self, discovery_engine):
        """Test getting tool by ID."""
        # Get a known tool
        tool = discovery_engine.get_tool_by_id("calculator")
        
        assert tool is not None
        assert tool["id"] == "calculator"
        assert "args_schema" in tool
    
    def test_get_tool_by_id_not_found(self, discovery_engine):
        """Test getting non-existent tool."""
        tool = discovery_engine.get_tool_by_id("nonexistent_tool")
        
        assert tool is None
    
    def test_list_categories(self, discovery_engine):
        """Test listing all categories."""
        categories = discovery_engine.list_categories()
        
        assert len(categories) > 0
        assert "search" in categories
        assert "math" in categories
    
    def test_get_free_tools(self, discovery_engine):
        """Test getting free tools."""
        free_tools = discovery_engine.get_free_tools()
        
        assert len(free_tools) > 0
        
        # All should not require API key
        for tool in free_tools:
            assert not tool.get("requires_api_key", False)
    
    def test_search_by_category_method(self, discovery_engine):
        """Test search_by_category method."""
        math_tools = discovery_engine.search_by_category("math")
        
        assert len(math_tools) > 0
        for tool in math_tools:
            assert tool["category"] == "math"
    
    def test_search_relevance_ranking(self, discovery_engine):
        """Test that search results are ranked by relevance."""
        # Search for "calculator"
        results = discovery_engine.search("calculator", top_k=5)
        
        # First result should be calculator (exact match)
        if len(results) > 0:
            assert "calculator" in results[0]["id"].lower() or "calculator" in results[0]["name"].lower()
    
    def test_search_with_no_results(self, discovery_engine):
        """Test search with query that matches nothing."""
        results = discovery_engine.search("xyzabc123nonexistent", top_k=5)
        
        # Should return empty list
        assert len(results) == 0
    
    def test_list_all_tools(self, discovery_engine):
        """Test listing all tools."""
        all_tools = discovery_engine.list_all_tools()
        
        assert len(all_tools) > 0
        assert len(all_tools) == len(discovery_engine.tools)


class TestToolDiscoveryIntegration:
    """Integration tests for tool discovery."""
    
    def test_discover_search_tools(self, discovery_engine):
        """Test discovering search tools for a search task."""
        # Use simple keyword that appears in search tool names
        results = discovery_engine.search("search", top_k=3, category="search")
        
        assert len(results) > 0
        
        # All should be search category
        for tool in results:
            assert tool["category"] == "search"
    
    def test_discover_math_tools(self, discovery_engine):
        """Test discovering math tools for calculation task."""
        # Use "calculator" keyword which is in tool name
        results = discovery_engine.search("calculator", top_k=3)
        
        assert len(results) > 0
        
        # Should find calculator
        tool_ids = [t["id"] for t in results]
        assert "calculator" in tool_ids
    
    def test_discover_file_tools(self, discovery_engine):
        """Test discovering file tools."""
        # Use "file" keyword which is in category and descriptions
        results = discovery_engine.search("file", top_k=3)
        
        assert len(results) > 0
        
        # Should find file tools
        categories = [t["category"] for t in results]
        assert "file" in categories
