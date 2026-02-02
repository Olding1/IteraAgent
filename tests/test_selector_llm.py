import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, ".")

from src.core.tool_selector import ToolSelector
from src.llm.builder_client import BuilderClient
from src.schemas.project_meta import ProjectMeta


async def test_selection():
    print("🧪 Testing Tool Selector (2-Stage Rerank)...")

    client = BuilderClient.from_env()
    selector = ToolSelector(client)

    # Test Case 1: Simple Search
    print("\n[Case 1] Search Request")
    meta = ProjectMeta(
        agent_name="TestAgent1",
        description="Search for weather",
        user_intent_summary="Help me search for today's weather in Tokyo",
        task_type="search",
    )

    config = await selector.select_tools(meta)
    print(f"Selected: {config.enabled_tools}")

    # Test Case 2: Math Request
    print("\n[Case 2] Math Request")
    meta2 = ProjectMeta(
        agent_name="TestAgent2",
        description="Calculate sine wave",
        user_intent_summary="Help me plot a sine wave",
        task_type="analysis",
    )
    config2 = await selector.select_tools(meta2)
    print(f"Selected: {config2.enabled_tools}")

    # Test Case 3: Complex ambiguity
    print("\n[Case 3] Ambiguous Request (Write python code to search?)")
    meta3 = ProjectMeta(
        agent_name="TestAgent3",
        description="Research assistant",
        user_intent_summary="Write a python script to search for latest AI papers",
        task_type="analysis",
    )
    config3 = await selector.select_tools(meta3)
    print(f"Selected: {config3.enabled_tools}")


if __name__ == "__main__":
    try:
        asyncio.run(test_selection())
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
