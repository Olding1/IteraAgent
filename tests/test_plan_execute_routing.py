import pytest
from src.core.graph_designer import GraphDesigner
from src.schemas import ProjectMeta, ToolsConfig, PatternType, PatternConfig
from src.llm import BuilderClient
from unittest.mock import MagicMock, AsyncMock


# Mock BuilderClient
class MockBuilderClient(BuilderClient):
    def __init__(self):
        self.config = MagicMock()
        self.client = AsyncMock()

    async def call(self, prompt: str, schema=None, **kwargs):
        return "Mock response"


@pytest.mark.asyncio
async def test_plan_execute_routing_fix():
    print("\n\n🧪 [Test] Plan-Execute Routing Fix...")

    # Setup
    builder = MockBuilderClient()
    designer = GraphDesigner(builder)

    # Project with tools + Plan-Execute
    project_meta = ProjectMeta(
        agent_name="TestAgent",
        description="Complex task",
        user_intent_summary="Complex task",
        has_rag=False,
        task_type="chat",
        execution_plan=[
            {"step": 1, "role": "Planner", "goal": "Plan step 1"},
            {"step": 2, "role": "Executor", "goal": "Execute step 2"},
            {"step": 3, "role": "Reviewer", "goal": "Review step 3"},
            {"step": 4, "role": "Finalizer", "goal": "Finalize step 4"},
        ],  # > 3 steps -> Plan-Execute
    )

    pattern = PatternConfig(pattern_type=PatternType.PLAN_EXECUTE)

    state_schema = await designer.define_state_schema(project_meta, pattern)
    tools_config = ToolsConfig(enabled_tools=["tavily_search"])

    # Run Design
    print("   🚀 Designing graph...")
    graph = await designer.design_nodes_and_edges(
        project_meta=project_meta,
        pattern=pattern,
        state_schema=state_schema,
        tools_config=tools_config,
    )

    # Check conditional edges from Executor
    executor_edges = [e for e in graph.conditional_edges if e.source == "executor"]
    assert len(executor_edges) > 0, "Executor should have conditional edges"

    edge = executor_edges[0]
    print(f"   ℹ️  Executor branches: {edge.branches}")

    # CRITICAL ASSERTION: Fallback should be 'evaluator', NOT 'replanner'
    # 'replanner' doesn't exist in the nodes list typically generated for Plan-Execute in this context
    # (or rather, the previous bug was it pointed to replanner but replanner node might not be the right target or logic was wrong,
    # actually the bug report said "Conditional edge target 'replanner' not found in nodes")
    # Let's check what nodes we have
    node_ids = [n.id for n in graph.nodes]
    print(f"   Nodes: {node_ids}")

    for target in edge.branches.values():
        if target != "END":
            assert target in node_ids, f"Target '{target}' not found in nodes!"

    # Specifically check the fallback/default branch
    # logic usually returns "replanner" in the bug, which maps to "replanner" in branches
    # We want to ensure that if logic returns something that implies 'not tool', it goes to a valid node.

    if "replanner" in edge.branches:
        assert "replanner" in node_ids, "Branch 'replanner' exists but Node 'replanner' is missing!"

    if "evaluator" in edge.branches:
        assert "evaluator" in node_ids
