"""Simulator - Blueprint Simulation Module.

This module simulates agent execution flow before code generation,
allowing early detection of logic issues like infinite loops.
"""

import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from types import SimpleNamespace

# 🔧 Debug flag - set to False to disable hybrid simulation debug logs
DEBUG_HYBRID = False

from ..schemas import (
    GraphStructure,
    SimulationResult,
    SimulationStep,
    SimulationIssue,
    SimulationStepType,
    StateField,
)
from ..llm import BuilderClient


class Simulator:
    """Simulator performs blueprint simulation of graph structures.
    
    🆕 v8.0 Hybrid Simulation:
    - LLM generates state (content, tool_calls)
    - Code executes routing (condition_logic)
    
    The Simulator:
    1. Simulates graph execution with sample input
    2. Tracks state changes through each node
    3. Detects logic issues (infinite loops, unreachable nodes)
    4. Generates execution traces and visualizations
    """
    
    def __init__(self, llm_client: BuilderClient, hybrid_mode: bool = True):
        """Initialize Simulator with LLM client.
        
        Args:
            llm_client: LLM client for simulating node execution
            hybrid_mode: Enable hybrid simulation (LLM state + code routing)
        """
        self.llm = llm_client
        self.hybrid_mode = hybrid_mode
    
    async def simulate(
        self,
        graph: GraphStructure,
        sample_input: str,
        max_steps: int = 20,
        use_llm: bool = True
    ) -> SimulationResult:
        """Simulate graph execution.
        
        Args:
            graph: Graph structure to simulate
            sample_input: Sample user input
            max_steps: Maximum simulation steps
            use_llm: Whether to use real LLM for node simulation (default: True)
            
        Returns:
            SimulationResult with execution trace and issues
        """
        # Initialize state
        state = self._initialize_state(graph.state_schema)
        state["messages"] = [{"role": "user", "content": sample_input}]
        
        # Simulation log
        steps: List[SimulationStep] = []
        visited_nodes: Dict[str, int] = {}
        
        # Start from entry point
        current_node = graph.entry_point
        step_count = 0
        
        while step_count < max_steps:
            step_count += 1
            
            # Track node visits
            visited_nodes[current_node] = visited_nodes.get(current_node, 0) + 1
            
            # Check for infinite loop
            if visited_nodes[current_node] > 5:
                steps.append(SimulationStep(
                    step_number=step_count,
                    step_type=SimulationStepType.ENTER_NODE,
                    node_id=current_node,
                    description=f"⚠️ 检测到无限循环：节点 {current_node} 访问超过5次",
                    state_snapshot=state.copy()
                ))
                break
            
            # Enter node
            steps.append(SimulationStep(
                step_number=step_count,
                step_type=SimulationStepType.ENTER_NODE,
                node_id=current_node,
                description=f"进入节点: {current_node}",
                state_snapshot=state.copy()
            ))
            
            # Find node definition
            node_def = self._find_node(graph, current_node)
            if not node_def:
                break
            
            # Simulate node execution
            state = await self._simulate_node(node_def, state, sample_input, graph, use_llm)
            
            # Exit node
            steps.append(SimulationStep(
                step_number=step_count + 0.5,
                step_type=SimulationStepType.EXIT_NODE,
                node_id=current_node,
                description=f"退出节点: {current_node}",
                state_snapshot=state.copy()
            ))
            
            # Determine next node
            next_node = self._get_next_node(graph, current_node, state)
            
            if next_node == "END" or next_node is None:
                steps.append(SimulationStep(
                    step_number=step_count + 1,
                    step_type=SimulationStepType.EDGE_TRAVERSE,
                    description="到达终点 END",
                    state_snapshot=state.copy()
                ))
                break
            
            # Traverse edge
            steps.append(SimulationStep(
                step_number=step_count + 1,
                step_type=SimulationStepType.EDGE_TRAVERSE,
                description=f"从 {current_node} 到 {next_node}",
                state_snapshot=state.copy()
            ))
            
            current_node = next_node
        
        # Detect issues
        issues = self.detect_issues(steps, graph, visited_nodes)
        
        # Generate traces
        execution_trace = self.generate_readable_log(steps)
        mermaid_trace = self.generate_mermaid_trace(steps, graph)
        
        # Determine success
        success = len(issues) == 0 or not any(i.severity == "error" for i in issues)
        
        return SimulationResult(
            success=success,
            total_steps=len(steps),
            steps=steps,
            issues=issues,
            final_state=state,
            execution_trace=execution_trace,
            mermaid_trace=mermaid_trace,
            simulated_at=datetime.now()
        )
    
    def _initialize_state(self, state_schema) -> Dict[str, Any]:
        """Initialize state with default values."""
        state = {}
        
        for field in state_schema.fields:
            if field.default is not None:
                state[field.name] = field.default
            elif field.type.value == "List[BaseMessage]":
                state[field.name] = []
            elif field.type.value == "List[str]":
                state[field.name] = []
            elif field.type.value == "Dict[str, Any]":
                state[field.name] = {}
            elif field.type.value == "int":
                state[field.name] = 0
            elif field.type.value == "bool":
                state[field.name] = False
            else:
                state[field.name] = None
        
        return state
    
    def _find_node(self, graph: GraphStructure, node_id: str):
        """Find node definition by ID."""
        for node in graph.nodes:
            if node.id == node_id:
                return node
        return None
    
    # ==================== 🆕 Hybrid Simulation Methods ====================
    
    async def _generate_llm_state(
        self,
        node_def,
        state: Dict[str, Any],
        sample_input: str,
        available_tools: List[str]
    ) -> Dict[str, Any]:
        """🆕 Hybrid Simulation: LLM generates state only (not routing).
        
        This method asks the LLM to generate the output content and tool_calls,
        but does NOT ask it to decide the next node. Routing is handled by
        deterministic code execution in _execute_condition_logic.
        
        Args:
            node_def: Node definition
            state: Current state
            sample_input: User input
            available_tools: List of available tool names
            
        Returns:
            Dict with keys: content, tool_calls
        """
        role_desc = node_def.role_description or f"You are {node_def.id}"
        
        # Build tools context
        tools_context = ""
        if available_tools:
            tools_context = f"\nAvailable Tools: {json.dumps(available_tools)}"
        
        # 🔍 Check if tools were already called in previous messages
        tool_already_called = False
        has_tool_results = False
        if state.get("messages"):
            if DEBUG_HYBRID:
                print(f"[DEBUG Hybrid] Checking {len(state['messages'])} messages for tool usage:")
            for i, msg in enumerate(state["messages"]):
                msg_type = type(msg).__name__
                has_tc = hasattr(msg, "tool_calls") and msg.tool_calls
                is_tool_msg = (hasattr(msg, "type") and msg.type == "tool") or (isinstance(msg, dict) and msg.get("type") == "tool")
                
                if DEBUG_HYBRID:
                    print(f"[DEBUG Hybrid]   Msg {i}: type={msg_type}, has_tool_calls={has_tc}, is_tool_message={is_tool_msg}")
                
                # Check if any previous message called tools
                if has_tc:
                    tool_already_called = True
                    if DEBUG_HYBRID:
                        print(f"[DEBUG Hybrid]     → Found tool_calls: {msg.tool_calls if hasattr(msg, 'tool_calls') else 'N/A'}")
                # Check if we have tool results (ToolMessage)
                if is_tool_msg:
                    has_tool_results = True
                    if DEBUG_HYBRID:
                        print(f"[DEBUG Hybrid]     → Found tool result message")
            
            if DEBUG_HYBRID:
                print(f"[DEBUG Hybrid] Summary: tool_already_called={tool_already_called}, has_tool_results={has_tool_results}")
        
        # 🆕 Add context about tool usage
        tool_usage_hint = ""
        if tool_already_called and has_tool_results:
            tool_usage_hint = f"""
**IMPORTANT - Tool Already Called**:
- You have ALREADY called tools in previous steps
- Tool results are available in the message history
- DO NOT call tools again - use the results to generate your FINAL ANSWER
- Set tool_calls to [] (empty array)
"""
            if DEBUG_HYBRID:
                print(f"[DEBUG Hybrid] Adding STOP hint to LLM prompt")
        elif tool_already_called and not has_tool_results:
            tool_usage_hint = f"""
**Note**: Tools were called but results not yet received.
"""
            if DEBUG_HYBRID:
                print(f"[DEBUG Hybrid] Tools called but no results yet")
        
        prompt = f"""You are simulating an LLM node in a LangGraph agent.

Node: {node_def.id}
Role: {role_desc}
Current State: {self._format_state_for_llm(state)}

User Input: {sample_input}
{tools_context}
{tool_usage_hint}

**Task**: Generate the LLM's output (NOT routing decision).

Output JSON:
{{
    "content": "your response message",
    "tool_calls": [  // Include ONLY if you need to call a tool
        {{"name": "exact_tool_name", "args": {{}}}}
    ]
}}

**Critical Rules**:
1. Check message history - if tools were already called and you have results, DO NOT call again
2. If user asks to search/find/query AND no tool was called yet, you MUST include tool_calls
3. Use EXACT tool name from available tools: {available_tools}
4. If no tool needed OR tool already called, omit tool_calls or set to []

**Examples**:
- First call + User: "Search for AI news" + Tools: ["tavily_search"]
  → {{"content": "Searching...", "tool_calls": [{{"name": "tavily_search", "args": {{}}}}]}}
  
- After tool results received + User: "Search for AI news"
  → {{"content": "Based on the search results: [summary]", "tool_calls": []}}
  
- User: "Hello" + Tools: []
  → {{"content": "Hi! How can I help?", "tool_calls": []}}
"""
        
        response = await self.llm.call(prompt)
        
        # Parse JSON
        try:
            json_str = response
            if "```json" in response:
                match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
                if match:
                    json_str = match.group(1)
            elif "{" in response:
                match = re.search(r'{.*}', response, re.DOTALL)
                if match:
                    json_str = match.group(0)
            
            data = json.loads(json_str)
            
            return {
                "content": data.get("content", ""),
                "tool_calls": data.get("tool_calls", [])
            }
        except Exception as e:
            print(f"[ERROR] Failed to parse LLM response: {e}")
            print(f"[ERROR] Response was: {response[:200]}...")
            return {"content": response, "tool_calls": []}
    
    def _execute_condition_logic(
        self,
        cond_edge,
        state: Dict[str, Any]
    ) -> Optional[str]:
        """🆕 Hybrid Simulation: Execute deterministic condition logic.
        
        This method executes the condition_logic code (generated by GraphDesigner)
        to determine the next node. This ensures simulation behavior matches
        runtime behavior exactly.
        
        Args:
            cond_edge: ConditionalEdgeDef
            state: Current state
            
        Returns:
            Next node ID, or None if execution failed
        """
        if not cond_edge.condition_logic:
            return None
        
        try:
            # Wrap condition logic in a function
            # Indent each line of user logic with 4 spaces
            indented_logic = '\n'.join('    ' + line for line in cond_edge.condition_logic.split('\n'))
            
            # 🔍 Debug: Print state before execution
            print(f"[DEBUG Hybrid] State before condition_logic execution:")
            if "messages" in state and state["messages"]:
                last_msg = state["messages"][-1]
                print(f"[DEBUG Hybrid]   Last message type: {type(last_msg)}")
                print(f"[DEBUG Hybrid]   Has tool_calls attr: {hasattr(last_msg, 'tool_calls')}")
                if hasattr(last_msg, 'tool_calls'):
                    print(f"[DEBUG Hybrid]   tool_calls value: {last_msg.tool_calls}")
                    print(f"[DEBUG Hybrid]   tool_calls type: {type(last_msg.tool_calls)}")
                    print(f"[DEBUG Hybrid]   tool_calls bool: {bool(last_msg.tool_calls)}")
            
            wrapped_code = f"""
def check_condition(state):
    # Safe imports
    import json
    from types import SimpleNamespace
    
    # User logic
{indented_logic}
"""
            
            # 🔍 Debug: Print the actual code being executed
            print(f"[DEBUG Hybrid] Executing wrapped code:")
            print(wrapped_code)
            print(f"[DEBUG Hybrid] End of wrapped code\n")
            
            # Execute
            exec_globals = {}
            exec(wrapped_code, exec_globals)
            
            check_condition = exec_globals['check_condition']
            result = check_condition(state)
            
            print(f"[DEBUG Hybrid] condition_logic returned: '{result}'")
            
            # Validate result is in branches
            if result in cond_edge.branches:
                next_node = cond_edge.branches[result]
                print(f"[DEBUG Hybrid] ✅ Deterministic routing: {result} → {next_node}")
                return next_node
            else:
                print(f"[WARNING Hybrid] Result '{result}' not in branches: {cond_edge.branches}")
                return None
                
        except Exception as e:
            print(f"[ERROR Hybrid] condition_logic execution failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    # ==================== End Hybrid Simulation Methods ====================
    
    async def _simulate_node(
        self,
        node_def,
        state: Dict[str, Any],
        sample_input: str,
        graph: GraphStructure,
        use_llm: bool = True
    ) -> Dict[str, Any]:
        """Simulate node execution.
        
        🆕 Hybrid Mode: Uses _generate_llm_state for LLM nodes
        Legacy Mode: Uses old prompt-based simulation
        """
        if node_def.type == "llm" and use_llm:
            # 🆕 Hybrid Simulation Mode
            if self.hybrid_mode:
                try:
                    # Step 1: Find available tools
                    available_tools = self._find_tool_nodes(node_def, graph)
                    
                    # Step 2: LLM generates state only (not routing)
                    llm_output = await self._generate_llm_state(
                        node_def, state, sample_input, available_tools
                    )
                    
                    print(f"[DEBUG Hybrid] LLM Output: content={llm_output['content'][:50]}..., tool_calls={llm_output['tool_calls']}")
                    
                    # Step 3: Construct message object (standard format)
                    msg = SimpleNamespace(
                        role="assistant",
                        content=llm_output["content"],
                        tool_calls=llm_output["tool_calls"],
                        type="ai"
                    )
                    
                    state["messages"].append(msg)
                    
                    # Update pattern-specific fields
                    if "draft" in state:
                        state["draft"] = llm_output["content"]
                    if "feedback" in state and "critic" in node_def.id.lower():
                        state["feedback"] = llm_output["content"]
                        
                except Exception as e:
                    print(f"[ERROR Hybrid] LLM simulation failed: {e}")
                    state["messages"].append(SimpleNamespace(
                        role="assistant",
                        content=f"[Sim Error] {node_def.id}",
                        tool_calls=[],
                        type="ai"
                    ))
            
            # Legacy Simulation Mode (for backward compatibility)
            else:
                try:
                    # 1. Find potential tool nodes connected to this node
                    available_tools = self._find_tool_nodes(node_def, graph)
                    tools_context = ""
                    if available_tools:
                        tools_context = f"\\nAvailable Tools: {json.dumps(available_tools)}\\n(If you need to search or perform actions, use one of these tool names in 'tool_name')"

                    # 2. Build Prompt
                    role_desc = node_def.role_description or f"You are {node_def.id} node"
                    
                    prompt = f"""You are simulating the execution of a LangGraph node.

Node: {node_def.id}
Role: {role_desc}
Current State: {self._format_state_for_llm(state)}

User Input: {sample_input}
{tools_context}

Determine the next action for this node.
Output ONLY a JSON object with this structure:
{{
    "thought": "Brief analysis of the situation",
    "action": "call_tool" or "reply",
    "tool_name": "name of tool to call (optional)",
    "content": "Response message content"
}}

Rules:
1. If the node should use a tool (search, calculation, etc.), set "action" to "call_tool" and provide the EXACT "tool_name" from the available tools list.
2. If the user explicitly asks to search/find/query, you MUST set "action" to "call_tool".
3. Otherwise, set "action" to "reply".
"""
                    response = await self.llm.call(prompt=prompt)
                    
                    # 3. Parse and Handle Response
                    try:
                        print(f"\n[DEBUG Simulator] Node: {node_def.id}")
                        if available_tools:
                            print(f"[DEBUG Simulator] Available Tools detected: {available_tools}")
                        else:
                            print(f"[DEBUG Simulator] NO Available Tools detected!")
                        
                        print(f"[DEBUG Simulator] LLM Raw Response: {response[:200]}...")
                        
                        # Extract JSON
                        json_str = response
                        if "```json" in response:
                            match = re.search(r'```json\s*({.*?})\s*```', response, re.DOTALL)
                            if match:
                                json_str = match.group(1)
                        elif "{" in response:
                            match = re.search(r'{.*}', response, re.DOTALL)
                            if match:
                                json_str = match.group(0)
                        
                        print(f"[DEBUG Simulator] Extracted JSON: {json_str[:200]}...")
                        data = json.loads(json_str)
                        print(f"[DEBUG Simulator] Parsed Data: {data}")
                        
                        action = data.get("action", "reply")
                        content = data.get("content", str(data))
                        tool_calls = []
                        
                        print(f"[DEBUG Simulator] Action: {action}")
                        
                        if action == "call_tool":
                            target_tool = data.get("tool_name", "")
                            print(f"[DEBUG Simulator] Target Tool from LLM: '{target_tool}'")
                            
                            # 4. Robust Fallback / Validation
                            matched_tool = None
                            
                            if available_tools:
                                # Try exact match
                                if target_tool in available_tools:
                                    matched_tool = target_tool
                                    print(f"[DEBUG Simulator] ✅ Exact match found: {matched_tool}")
                                else:
                                    # Try fuzzy match / simple heuristic
                                    for tool in available_tools:
                                        if target_tool in tool or tool in target_tool:
                                            matched_tool = tool
                                            print(f"[DEBUG Simulator] ✅ Fuzzy match found: {matched_tool}")
                                            break
                                    
                                    # If still no match, but LLM said 'search' and we have a search tool
                                    if not matched_tool and ("search" in target_tool.lower() or target_tool == ""):
                                        matched_tool = available_tools[0]
                                        print(f"[DEBUG Simulator] ✅ Fallback to first tool: {matched_tool}")
                            
                            if matched_tool:
                                tool_calls.append({"name": matched_tool, "args": {}})
                                print(f"[DEBUG Simulator] ✅ Added tool_call: {tool_calls}")
                            elif target_tool:
                                 tool_calls.append({"name": target_tool, "args": {}})
                                 print(f"[DEBUG Simulator] ⚠️ Added unmatched tool_call: {tool_calls}")
                        else:
                            print(f"[DEBUG Simulator] ℹ️ Action is '{action}', no tool call")
                        
                        # Create Message Object
                        msg = SimpleNamespace(
                            role="assistant",
                            content=content,
                            tool_calls=tool_calls,
                            type="ai"
                        )
                        print(f"[DEBUG Simulator] Created message with tool_calls: {msg.tool_calls}")
                        state["messages"].append(msg)
                        
                        if "draft" in state:
                            state["draft"] = content
                        if "feedback" in state and "critic" in node_def.id.lower():
                            state["feedback"] = content
                            
                    except Exception as parse_error:
                        print(f"[DEBUG Simulator] ❌ Parse error: {parse_error}")
                        state["messages"].append(SimpleNamespace(role="assistant", content=response, tool_calls=[], type="ai"))
                    
                except Exception as e:
                    state["messages"].append(SimpleNamespace(role="assistant", content=f"[Sim] {node_def.id}", tool_calls=[], type="ai"))
        
        elif node_def.type == "llm":
            # Heuristic simulation for LLM nodes
            state["messages"].append({
                "role": "assistant",
                "content": f"[模拟] {node_def.id} 的响应"
            })
            
            # Update pattern-specific fields
            if "draft" in state:
                state["draft"] = f"Draft from {node_def.id}"
            if "feedback" in state:
                state["feedback"] = f"Feedback from {node_def.id}"
        
        elif node_def.type == "tool":
            # Simulate tool execution
            tool_name = node_def.config.get("tool_name", "unknown") if node_def.config else "unknown"
            state["tool_results"] = state.get("tool_results", {})
            state["tool_results"][tool_name] = f"[模拟] {tool_name} 结果"
            
            # 🆕 Add ToolMessage to messages so LLM can detect tool was called
            tool_message = SimpleNamespace(
                type="tool",
                role="tool",
                content=f"[模拟] {tool_name} 返回结果: 搜索完成，找到相关信息",
                tool_call_id="simulated_call"
            )
            state["messages"].append(tool_message)
            print(f"[DEBUG Hybrid] Added ToolMessage for {tool_name}")
        
        elif node_def.type == "rag":
            # Simulate RAG retrieval
            state["retrieved_docs"] = ["Doc1", "Doc2", "Doc3"]
            state["context"] = "[模拟] RAG上下文"
            
            # Add ToolMessage to indicate RAG has been called (Router Pattern)
            state["messages"].append({
                "type": "tool",
                "role": "tool",
                "content": "[模拟] RAG检索结果: 找到3个相关文档"
            })
        
        # Update iteration count if exists
        if "iteration_count" in state:
            state["iteration_count"] += 1
        
        # Update current step if exists
        if "current_step" in state:
            state["current_step"] += 1
        
        return state
    
    def _format_state_for_llm(self, state: Dict[str, Any]) -> str:
        """Format state for LLM prompt."""
        # Only include key fields, avoid verbose data
        formatted = {}
        for key, value in state.items():
            if key == "messages":
                formatted[key] = f"{len(value)} messages"
            elif isinstance(value, (str, int, bool)):
                formatted[key] = value
            elif isinstance(value, list):
                formatted[key] = f"[{len(value)} items]"
            elif isinstance(value, dict):
                formatted[key] = f"{{...}}"
        
        return str(formatted)
    
    def _get_next_node(
        self,
        graph: GraphStructure,
        current_node: str,
        state: Dict[str, Any]
    ) -> Optional[str]:
        """Determine next node based on edges."""
        print(f"\n[DEBUG Simulator] _get_next_node from: {current_node}")
        
        # Check conditional edges first
        for cond_edge in graph.conditional_edges:
            if cond_edge.source == current_node:
                print(f"[DEBUG Simulator] Found conditional edge from {current_node}")
                print(f"[DEBUG Simulator] Branches: {cond_edge.branches}")
                # Evaluate condition
                next_node = self._evaluate_condition(cond_edge, state)
                if next_node:
                    print(f"[DEBUG Simulator] ✅ Conditional edge resolved to: {next_node}")
                    return next_node
        
        # Check regular edges
        for edge in graph.edges:
            if edge.source == current_node:
                print(f"[DEBUG Simulator] ✅ Regular edge to: {edge.target}")
                return edge.target
        
        # No edge found, assume END
        print(f"[DEBUG Simulator] ⚠️ No edge found, returning END")
        return "END"
    
    def _evaluate_condition(self, cond_edge, state: Dict[str, Any]) -> Optional[str]:
        """Evaluate conditional edge.
        
        🆕 Hybrid Mode: Prioritize deterministic condition_logic execution
        Legacy Mode: Falls back to heuristic evaluation
        """
        # 🆕 Hybrid Simulation Mode
        if self.hybrid_mode:
            # Priority 1: Execute condition_logic (deterministic)
            next_node = self._execute_condition_logic(cond_edge, state)
            if next_node:
                return next_node
            
            # Priority 2: Conservative fallback
            # If condition_logic failed, default to "end" branch
            print(f"[WARNING Hybrid] condition_logic failed, using conservative fallback")
            
            if "end" in cond_edge.branches:
                return cond_edge.branches["end"]
            
            # If no end branch, return first branch (last resort)
            if cond_edge.branches:
                fallback = list(cond_edge.branches.values())[0]
                print(f"[WARNING Hybrid] No 'end' branch, fallback to: {fallback}")
                return fallback
            
            return "END"
        
        # Legacy Mode: Original implementation
        if cond_edge.condition_logic:
            try:
                # Wrap condition logic in a function to return value
                wrapped_code = f"""
def check_condition(state):
    # Safe globals
    import json
    
    # User logic
{'\n'.join('    ' + line for line in cond_edge.condition_logic.split('\n'))}
"""
                # Create execution environment
                exec_globals = {}
                exec(wrapped_code, exec_globals)
                
                # Execute the function
                check_condition = exec_globals['check_condition']
                result = check_condition(state)
                
                if result in cond_edge.branches:
                    return cond_edge.branches[result]
                    
            except Exception as e:
                print(f"Warning: Failed to execute condition_logic: {e}")
        
        # Fallback to heuristic evaluation
        return self._heuristic_evaluate_condition(cond_edge, state)
    
    def _heuristic_evaluate_condition(self, cond_edge, state: Dict[str, Any]) -> Optional[str]:
        """Heuristic-based condition evaluation."""
        print(f"[DEBUG Simulator] _heuristic_evaluate_condition called")
        
        # 1. Check for tool calls in the last message (Priority)
        messages = state.get("messages", [])
        print(f"[DEBUG Simulator] Total messages in state: {len(messages)}")
        
        if messages:
            last_msg = messages[-1]
            print(f"[DEBUG Simulator] Last message type: {type(last_msg)}")
            print(f"[DEBUG Simulator] Last message attributes: {dir(last_msg) if hasattr(last_msg, '__dict__') else 'N/A'}")
            
            # Check if it has tool_calls (Namespace or dict)
            tool_calls = getattr(last_msg, "tool_calls", []) or []
            print(f"[DEBUG Simulator] tool_calls from last message: {tool_calls}")
            
            if tool_calls:
                # Get the first tool name
                # Handle both dict (from heuristic) and valid obj (from LLM)
                if isinstance(tool_calls[0], dict):
                    tool_name = tool_calls[0].get("name")
                else:
                     tool_name = tool_calls[0].name
                
                print(f"[DEBUG Simulator] Extracted tool_name: '{tool_name}'")
                print(f"[DEBUG Simulator] Available branches: {cond_edge.branches}")
                
                # Check if this tool is in branches
                if tool_name in cond_edge.branches:
                    result = cond_edge.branches[tool_name]
                    print(f"[DEBUG Simulator] ✅ Tool name matched! Returning: {result}")
                    return result
                else:
                    print(f"[DEBUG Simulator] ❌ Tool name '{tool_name}' NOT in branches!")

        # Check iteration count
        if "iteration_count" in state and "max_iterations" in state:
            if state["iteration_count"] >= state["max_iterations"]:
                return cond_edge.branches.get("end", "END")
            else:
                # Continue iteration
                for key in cond_edge.branches:
                    if key != "end":
                        return cond_edge.branches[key]
        
        # Check is_finished
        if state.get("is_finished", False):
            return cond_edge.branches.get("end", "END")
        
        # Check plan completion
        if "current_step" in state and "plan" in state:
            if state["current_step"] >= len(state["plan"]):
                return cond_edge.branches.get("end", "END")
        
        # Router Pattern: Check if RAG has been called
        if "search" in cond_edge.branches and "finish" in cond_edge.branches:
            # This is a Router Pattern conditional edge
            messages = state.get("messages", [])
            
            # Check if we have ToolMessage (RAG has been called)
            has_tool_message = any(
                isinstance(msg, dict) and msg.get("type") == "tool"
                for msg in messages
            )
            
            if has_tool_message:
                # RAG has been called, finish
                return cond_edge.branches.get("finish", "END")
            else:
                # First time, need to search
                return cond_edge.branches.get("search")
        
        # Default: return first non-end branch
        for key, value in cond_edge.branches.items():
            if key != "end":
                return value
        
        return "END"
    
    def detect_issues(
        self,
        simulation_log: List[SimulationStep],
        graph: GraphStructure,
        visited_nodes: Dict[str, int]
    ) -> List[SimulationIssue]:
        """Detect issues in simulation."""
        issues = []
        
        # Check for infinite loops
        for node_id, visit_count in visited_nodes.items():
            if visit_count > 5:
                issues.append(SimulationIssue(
                    issue_type="infinite_loop",
                    severity="error",
                    description=f"检测到无限循环：节点 '{node_id}' 被访问了 {visit_count} 次",
                    affected_nodes=[node_id],
                    suggestion="添加迭代计数器并设置最大迭代次数"
                ))
        
        # Check for unreachable nodes
        all_node_ids = {node.id for node in graph.nodes}
        visited_node_ids = set(visited_nodes.keys())
        unreachable = all_node_ids - visited_node_ids
        
        if unreachable:
            issues.append(SimulationIssue(
                issue_type="unreachable_node",
                severity="warning",
                description=f"发现不可达节点：{', '.join(unreachable)}",
                affected_nodes=list(unreachable),
                suggestion="检查边的连接是否正确"
            ))
        
        return issues
    
    def generate_mermaid_trace(
        self,
        simulation_log: List[SimulationStep],
        graph: GraphStructure
    ) -> str:
        """Generate Mermaid diagram of execution trace."""
        lines = ["graph LR"]
        
        # Track transitions
        transitions = []
        prev_node = None
        
        for step in simulation_log:
            if step.step_type == SimulationStepType.ENTER_NODE and step.node_id:
                if prev_node and prev_node != step.node_id:
                    transitions.append((prev_node, step.node_id))
                prev_node = step.node_id
        
        # Generate Mermaid syntax
        for i, (source, target) in enumerate(transitions):
            lines.append(f"    {source}[{source}] -->|{i+1}| {target}[{target}]")
        
        return "\n".join(lines)
    
    def _find_tool_nodes(self, current_node_def, graph: GraphStructure) -> List[str]:
        """Find tool nodes reachable from the current node."""
        tool_nodes = []
        
        # 1. Check conditional edges from this node
        for edge in graph.conditional_edges:
            if edge.source == current_node_def.id:
                # Collect tool names from branches
                for target_node_id in edge.branches.values():
                    # Check if target is a tool node
                    target_node = self._find_node(graph, target_node_id)
                    if target_node and target_node.type == "tool":
                         # Get tool name from config if available, else use node ID
                         tool_name = target_node.config.get("tool_name") if target_node.config else None
                         if not tool_name:
                             # Try to infer from node ID (e.g. tool_tavily_search -> tavily_search)
                             if target_node_id.startswith("tool_"):
                                 tool_name = target_node_id[5:]
                             else:
                                 tool_name = target_node_id
                         
                         tool_nodes.append(tool_name)
                         
        # 2. Check regular edges (less common for tool calling, usually conditional)
        for edge in graph.edges:
            if edge.source == current_node_def.id:
                target_node = self._find_node(graph, edge.target)
                if target_node and target_node.type == "tool":
                    tool_name = target_node.config.get("tool_name")
                    if not tool_name:
                        if edge.target.startswith("tool_"):
                            tool_name = edge.target[5:]
                        else:
                            tool_name = edge.target
                    tool_nodes.append(tool_name)
                    
        return list(set(tool_nodes))

    def generate_readable_log(
        self,
        simulation_log: List[SimulationStep]
    ) -> str:
        """Generate readable execution trace."""
        lines = ["=== 仿真执行轨迹 ===\n"]
        
        for step in simulation_log:
            step_num = int(step.step_number) if step.step_number == int(step.step_number) else step.step_number
            lines.append(f"Step {step_num}: {step.description}")
        
        return "\n".join(lines)
