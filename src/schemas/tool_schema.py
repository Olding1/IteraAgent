"""Tool schema definitions for IteraAgent v8.0.

This module defines the schema for tool definitions used in the tool discovery
and interface guard systems.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List


class ToolDefinition(BaseModel):
    """工具定义元数据

    用于工具索引和 Interface Guard 验证。
    """

    id: str = Field(..., description="工具唯一标识,如 'duckduckgo_search'")
    name: str = Field(..., description="工具显示名称,如 'DuckDuckGo Search'")
    description: str = Field(..., description="工具功能描述,用于语义搜索")

    # 安装信息
    package_name: str = Field(..., description="pip 包名,如 'duckduckgo-search'")
    import_path: str = Field(
        ..., description="导入路径,如 'langchain_community.tools.DuckDuckGoSearchRun'"
    )

    # 接口定义 (用于 Interface Guard)
    args_schema: Dict[str, Any] = Field(..., description="OpenAPI/JSON Schema 格式的参数定义")

    # 可选字段
    category: str = Field(
        default="general", description="工具分类: search, math, file, code, knowledge"
    )
    requires_api_key: bool = Field(default=False, description="是否需要 API Key")
    examples: List[Dict[str, Any]] = Field(
        default_factory=list, description="使用示例,格式为参数字典列表"
    )
    tags: List[str] = Field(default_factory=list, description="标签列表,用于搜索")


class ToolValidationError(BaseModel):
    """工具参数验证错误"""

    tool_name: str = Field(..., description="工具名称")
    error_type: str = Field(..., description="错误类型: missing_field, wrong_type, etc.")
    error_message: str = Field(..., description="错误详细信息")
    field_name: Optional[str] = Field(None, description="出错的字段名")
    expected: Optional[str] = Field(None, description="期望的值/类型")
    actual: Optional[str] = Field(None, description="实际的值/类型")


class ToolValidationResult(BaseModel):
    """工具参数验证结果"""

    is_valid: bool = Field(..., description="是否验证通过")
    tool_name: str = Field(..., description="工具名称")
    original_args: Dict[str, Any] = Field(..., description="原始参数")
    corrected_args: Optional[Dict[str, Any]] = Field(
        None, description="修正后的参数 (如果进行了修正)"
    )
    errors: List[ToolValidationError] = Field(default_factory=list, description="验证错误列表")
    retry_count: int = Field(default=0, description="重试次数")
