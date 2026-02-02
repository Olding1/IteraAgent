"""Tool Selector - Selects appropriate tools based on requirements."""

from typing import List, Optional, Dict
import json
import re

from ..schemas import ProjectMeta, ToolsConfig
from ..tools import ToolRegistry, get_global_registry
from ..llm import BuilderClient


class ToolSelector:
    """Tool Selector chooses appropriate tools based on project requirements.

    The Tool Selector is responsible for:
    1. Analyzing project requirements
    2. Matching requirements to available tools
    3. Selecting top-K most relevant tools
    4. Outputting ToolsConfig
    """

    def __init__(self, builder_client: BuilderClient, registry: Optional[ToolRegistry] = None):
        """Initialize Tool Selector.

        Args:
            builder_client: LLM client for tool selection
            registry: Tool registry (uses global if not provided)
        """
        self.builder = builder_client
        self.registry = registry or get_global_registry()

        # 🆕 v8.0: Tool Discovery Engine
        from .tool_discovery import ToolDiscoveryEngine

        self.discovery = ToolDiscoveryEngine()

    async def select_tools(self, project_meta: ProjectMeta, max_tools: int = 5) -> ToolsConfig:
        """Select tools based on project requirements.

        Using 2-stage architecture:
        1. Recall (Rough Search): Top-K from vector/keyword search
        2. Rerank (Fine-grained): LLM Judge
        """
        # --- Stage 1: Recall (粗筛) ---
        # Build search query
        query = f"{project_meta.description} {project_meta.user_intent_summary}"
        print(f"🔍 [ToolSelector] Query: '{query}'")

        # Get more candidates for LLM to choose from (e.g. 10)
        candidates = self.discovery.search(query, top_k=max_tools * 2)

        if not candidates:
            print("⚠️ [ToolSelector] 粗筛未找到任何工具")
            return ToolsConfig(enabled_tools=[])

        print(
            f"🔍 [ToolSelector] 粗筛候选项 ({len(candidates)}): {[t['name'] for t in candidates]}"
        )

        # --- Stage 2: Rerank (精排) ---
        try:
            selected_ids = await self._llm_rerank(project_meta, candidates, max_tools)
            print(f"🎯 [ToolSelector] 精排结果: {selected_ids}")
            return ToolsConfig(enabled_tools=selected_ids)
        except Exception as e:
            print(f"⚠️ [ToolSelector] LLM Rerank 失败, 回退到粗筛结果: {e}")
            import traceback

            traceback.print_exc()
            # Fallback: just return top max_tools from recall
            fallback_ids = [t["id"] for t in candidates[:max_tools]]
            return ToolsConfig(enabled_tools=fallback_ids)

    async def _llm_rerank(
        self, project_meta: ProjectMeta, candidates: List[Dict], max_tools: int
    ) -> List[str]:
        """Call LLM to rerank and select best tools."""

        # 1. Build candidate descriptions
        tools_desc = []
        for idx, tool in enumerate(candidates):
            # Format: 0. [Tavily Search] (id: tavily_search): Search the web...
            tools_desc.append(
                f"{idx}. [{tool['name']}] (id: {tool['id']}): {tool['description'][:200]}..."
            )

        tools_str = "\n".join(tools_desc)

        # 2. Build Prompt
        prompt = f"""You are an expert Tool Selector for an AI Agent.
Your task is to select the most appropriate tools from a candidate list to solve the user's request.

# Project Context
Agent Name: {project_meta.agent_name}
User Intent: "{project_meta.user_intent_summary}"
Process Description: "{project_meta.description}"
Task Type: {project_meta.task_type}

# Candidate Tools
{tools_str}

# Selection Rules (CRITICAL)
1. Analyze the user's intent carefully.
2. Select tools that are NECESSARY to solve the problem.
3. If multiple tools do similar things (e.g. Google vs DuckDuckGo), pick the most capable one (e.g. Tavily/Google over DuckDuckGo).
4. For searching news/events -> Prioritize 'Tavily Search' or 'Google Search'.
5. For math/data/plotting -> Prioritize 'Python REPL' (better than Calculator).
6. If NO tools are needed (e.g. pure chit-chat), return empty selection.
7. Select at most {max_tools} tools.

# Output Format
Return a JSON object with a single key "selected_indices".
Example: {{ "selected_indices": [0, 2] }}
"""

        # 3. Call LLM
        response = await self.builder.call(prompt)

        # 4. Parse JSON

        # Clean markdown if present
        json_str = response.replace("```json", "").replace("```", "").strip()
        # Find JSON object
        match = re.search(r"\{.*\}", json_str, re.DOTALL)
        if match:
            json_str = match.group(0)

        try:
            result = json.loads(json_str)
            indices = result.get("selected_indices", [])

            # 5. Map back to IDs
            selected_ids = []
            for idx in indices:
                if isinstance(idx, int) and 0 <= idx < len(candidates):
                    # Prevent duplicates
                    tid = candidates[idx]["id"]
                    if tid not in selected_ids:
                        selected_ids.append(tid)

            return selected_ids
        except json.JSONDecodeError:
            print(f"❌ [ToolSelector] JSON Decode Error: {response}")
            raise

    def save_config(self, config: ToolsConfig, output_path) -> None:
        """Save tools config to JSON file.

        Args:
            config: ToolsConfig to save
            output_path: Path to save JSON file
        """
        from pathlib import Path

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(config.model_dump_json(indent=2))

    def load_config(self, input_path) -> ToolsConfig:
        """Load tools config from JSON file.

        Args:
            input_path: Path to JSON file

        Returns:
            ToolsConfig object
        """
        from pathlib import Path

        input_path = Path(input_path)

        with open(input_path, "r", encoding="utf-8") as f:
            return ToolsConfig.model_validate_json(f.read())
