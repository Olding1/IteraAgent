"""
Dify Schema 定义

定义 Dify DSL 的数据结构
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional


class DifyNodeData(BaseModel):
    """Dify 节点数据"""

    title: str
    type: str  # start, llm, tool, knowledge-retrieval, if-else, answer, code
    desc: str = ""
    selected: bool = False

    # LLM 节点特有字段
    model: Optional[Dict[str, str]] = None  # {"provider": "openai", "name": "gpt-4o"}
    prompt_template: Optional[List[Dict[str, str]]] = None  # [{"role": "system", "text": "..."}]

    # Tool 节点特有字段
    provider_id: Optional[str] = None  # "tavily"
    tool_name: Optional[str] = None  # "tavily_search"
    tool_parameters: Optional[Dict[str, Any]] = None

    # Knowledge Retrieval 特有字段
    dataset_ids: Optional[List[str]] = None  # 知识库 ID (导出时留空)
    retrieval_mode: Optional[str] = None  # 只在 RAG 节点使用

    # Start 节点特有字段
    variables: Optional[List[Dict[str, Any]]] = None

    # Answer 节点特有字段
    answer: Optional[str] = None  # 输出变量引用

    # Code 节点特有字段
    code: Optional[str] = None  # Python 代码
    code_language: Optional[str] = None  # 只在 Code 节点使用
    outputs: Optional[Dict[str, Any]] = None  # 输出变量定义

    # If-Else 节点特有字段
    conditions: Optional[List[Dict[str, Any]]] = None  # 条件列表


class DifyNode(BaseModel):
    """Dify 节点"""

    id: str
    data: DifyNodeData
    position: Dict[str, int]  # {"x": 0, "y": 0}
    sourcePosition: str = "right"
    targetPosition: str = "left"
    width: int = 240
    height: int = 90


class DifyEdge(BaseModel):
    """Dify 连线"""

    id: str
    source: str
    target: str
    sourceHandle: Optional[str] = None  # 条件边需要
    targetHandle: Optional[str] = None
    type: str = "default"


class DifyGraph(BaseModel):
    """Dify Graph"""

    nodes: List[DifyNode]
    edges: List[DifyEdge]


class DifyWorkflow(BaseModel):
    """Dify Workflow"""

    graph: DifyGraph
    version: str = "0.1.0"


class DifyApp(BaseModel):
    """Dify App (顶层结构)"""

    app: Dict[str, Any]  # name, mode, icon, description
    kind: str = "app"
    version: str = "0.1.0"
    workflow: DifyWorkflow
