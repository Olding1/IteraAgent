import pytest
import asyncio
from src.core.simulator import Simulator
from src.schemas import (
    GraphStructure,
    NodeDef,
    EdgeDef,
    ConditionalEdgeDef,
    StateSchema,
    PatternConfig,
    PatternType,
)
from src.llm import BuilderClient
from unittest.mock import MagicMock, AsyncMock


class MockBuilderClient(BuilderClient):
    def __init__(self):
        self.config = MagicMock()
        self.client = AsyncMock()

    async def call(self, prompt: str, schema=None, **kwargs):
        # Return JSON structure as expected by new Simulator
        if "tools" in prompt.lower() or "tavily" in prompt.lower() or "search" in prompt.lower():
            return """```json
{
    "thought": "User wants to search for AI news.",
    "action": "call_tool",
    "tool_name": "tavily_search"
}
```"""
        return """```json
{
    "thought": "Just a generic response.",
    "action": "reply",
    "content": "Generic response"
}
```"""


@pytest.mark.asyncio
async def test_simulator_tool_reachability():
    print("\n\n🧪 [Test] Simulator Tool Reachability...")

    # Setup Simulator
    builder = MockBuilderClient()
    simulator = Simulator(builder)

    # Manually construct a Sequential Graph with a Tool
    # agent -> (cond) -> [tool | end]
    # tool -> agent

    nodes = [
        NodeDef(id="agent", type="llm", role_description="Agent"),
        NodeDef(id="tool_tavily", type="tool", config={"tool_name": "tavily_search"}),
    ]

    # Condition logic that simulator usually fails to trigger because it relies on 'tool_calls' attribute
    condition_logic = """
last_msg = state["messages"][-1]
if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
    return "tavily_search"
return "end"
"""

    cond_edges = [
        ConditionalEdgeDef(
            source="agent",
            condition="check_tool",
            condition_logic=condition_logic,
            branches={"tavily_search": "tool_tavily", "end": "END"},
        )
    ]

    edges = [EdgeDef(source="tool_tavily", target="agent")]

    from src.schemas import StateField, StateFieldType

    state_schema = StateSchema(
        fields=[StateField(name="messages", type=StateFieldType.LIST_MESSAGE, default=[])]
    )

    graph = GraphStructure(
        pattern=PatternConfig(pattern_type=PatternType.SEQUENTIAL),
        nodes=nodes,
        edges=edges,
        conditional_edges=cond_edges,
        entry_point="agent",
        state_schema=state_schema,
    )

    # Run Simulation
    print("   🚀 Running simulation...")
    result = await simulator.simulate(graph, "Search for AI news", max_steps=5)

    # Check execution trace
    print("\n   📜 Execution Trace:")
    print(result.execution_trace)

    # Check for unreachable nodes issue
    unreachable_issue = next((i for i in result.issues if i.issue_type == "unreachable_node"), None)

    if unreachable_issue:
        print(f"   ⚠️  Found Unreachable Issue: {unreachable_issue.description}")
        # We expect this to FAIL (be found) before the fix
        # And PASS (not found) after the fix
    else:
        print("   ✅ No Unreachable Issue found")

    # Check if tool was actually visited
    tool_visited = any(step.node_id == "tool_tavily" for step in result.steps)
    print(f"   Tool Visited: {tool_visited}")

    assert tool_visited, "Simulator failed to visit tool node (Logic didn't trigger 'tavily')"
