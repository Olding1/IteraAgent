"""Interface Guard - Parameter validation and auto-correction for tools.

This module implements the Interface Guard system that validates tool parameters
against their schemas and automatically corrects errors using LLM.
"""

import json
import re
from typing import Dict, Any, Tuple, Optional, List, Type
from pydantic import BaseModel, ValidationError, create_model, Field

from ..llm import BuilderClient
from ..schemas.tool_schema import ToolValidationResult, ToolValidationError


class InterfaceGuard:
    """接口卫士 - 验证和修复工具参数
    
    Interface Guard 在工具调用前验证参数,确保:
    1. 所有必填参数都存在
    2. 参数类型正确
    3. 参数值符合约束
    
    如果验证失败,会使用 LLM 自动修复参数 (最多重试 3 次)。
    """
    
    def __init__(self, builder_client: BuilderClient, max_retries: int = 3):
        """初始化 Interface Guard
        
        Args:
            builder_client: Builder LLM 客户端,用于参数修复
            max_retries: 最大重试次数
        """
        self.builder = builder_client
        self.max_retries = max_retries
    
    async def validate_and_fix(
        self,
        tool_name: str,
        args: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> ToolValidationResult:
        """验证工具参数,如果失败则自动修复
        
        Args:
            tool_name: 工具名称
            args: 待验证的参数
            schema: OpenAPI/JSON Schema
            
        Returns:
            ToolValidationResult 包含验证结果和修正后的参数
        """
        # 1. 首次验证
        is_valid, errors = self._validate_with_pydantic(args, schema)
        if is_valid:
            return ToolValidationResult(
                is_valid=True,
                tool_name=tool_name,
                original_args=args,
                corrected_args=args,
                errors=[],
                retry_count=0
            )
        
        # 2. 自动修复循环
        current_args = args.copy()
        all_errors = errors.copy()
        
        for attempt in range(self.max_retries):
            print(f"🔧 [Guard] 尝试修复 {tool_name} 参数 (第 {attempt + 1}/{self.max_retries} 次)")
            print(f"   错误: {errors[0].error_message if errors else 'Unknown'}")
            
            # 调用 LLM 修复
            corrected_args = await self._auto_correct(
                tool_name, current_args, schema, errors
            )
            
            # 验证修复结果
            is_valid, errors = self._validate_with_pydantic(corrected_args, schema)
            if is_valid:
                print(f"✅ [Guard] 参数修复成功")
                return ToolValidationResult(
                    is_valid=True,
                    tool_name=tool_name,
                    original_args=args,
                    corrected_args=corrected_args,
                    errors=[],
                    retry_count=attempt + 1
                )
            
            current_args = corrected_args
            all_errors.extend(errors)
        
        # 3. 修复失败
        print(f"❌ [Guard] 参数修复失败,已达最大重试次数")
        return ToolValidationResult(
            is_valid=False,
            tool_name=tool_name,
            original_args=args,
            corrected_args=current_args,
            errors=all_errors,
            retry_count=self.max_retries
        )
    
    def _validate_with_pydantic(
        self,
        args: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Tuple[bool, List[ToolValidationError]]:
        """使用 Pydantic 验证参数
        
        Args:
            args: 参数字典
            schema: JSON Schema
            
        Returns:
            (是否有效, 错误列表)
        """
        try:
            # 动态创建 Pydantic 模型
            model = self._create_pydantic_model(schema)
            model(**args)
            return True, []
        except ValidationError as e:
            # 解析 Pydantic 错误
            errors = []
            for error in e.errors():
                field_name = ".".join(str(loc) for loc in error["loc"])
                errors.append(ToolValidationError(
                    tool_name="",  # 会在外层填充
                    error_type=error["type"],
                    error_message=error["msg"],
                    field_name=field_name,
                    expected=str(error.get("ctx", {})),
                    actual=str(args.get(field_name, "missing"))
                ))
            return False, errors
        except Exception as e:
            # 其他错误
            return False, [ToolValidationError(
                tool_name="",
                error_type="validation_error",
                error_message=str(e),
                field_name=None,
                expected=None,
                actual=None
            )]
    
    def _create_pydantic_model(self, schema: Dict[str, Any]) -> Type[BaseModel]:
        """从 JSON Schema 创建 Pydantic 模型
        
        Args:
            schema: JSON Schema 定义
            
        Returns:
            动态创建的 Pydantic 模型类
        """
        fields = {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        for field_name, field_schema in properties.items():
            field_type = self._json_type_to_python(field_schema.get("type", "string"))
            description = field_schema.get("description", "")
            is_required = field_name in required
            
            if is_required:
                fields[field_name] = (field_type, Field(..., description=description))
            else:
                fields[field_name] = (Optional[field_type], Field(None, description=description))
        
        return create_model("DynamicToolArgs", **fields)
    
    def _json_type_to_python(self, json_type: str) -> type:
        """JSON Schema 类型转 Python 类型
        
        Args:
            json_type: JSON Schema 类型字符串
            
        Returns:
            对应的 Python 类型
        """
        type_mapping = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }
        return type_mapping.get(json_type, str)
    
    async def _auto_correct(
        self,
        tool_name: str,
        args: Dict[str, Any],
        schema: Dict[str, Any],
        errors: List[ToolValidationError]
    ) -> Dict[str, Any]:
        """使用 LLM 自动修复参数
        
        Args:
            tool_name: 工具名称
            args: 当前参数
            schema: 参数 Schema
            errors: 验证错误列表
            
        Returns:
            修正后的参数
        """
        # 格式化错误信息
        error_messages = "\n".join([
            f"- {err.error_message} (字段: {err.field_name})"
            for err in errors
        ])
        
        prompt = f"""你是一个参数修复助手。工具调用参数验证失败,请修正参数。

工具名称: {tool_name}

参数 Schema:
```json
{json.dumps(schema, indent=2, ensure_ascii=False)}
```

当前参数:
```json
{json.dumps(args, indent=2, ensure_ascii=False)}
```

验证错误:
{error_messages}

请分析错误原因,修正参数。注意:
1. 确保所有必填字段都存在
2. 确保字段类型正确
3. 不要添加 Schema 中未定义的字段

请输出修正后的参数 (仅输出 JSON,不要其他内容):
"""
        
        response = await self.builder.call(prompt=prompt)
        
        # 解析 LLM 返回的 JSON
        try:
            corrected_args = json.loads(response)
            return corrected_args
        except json.JSONDecodeError:
            # 如果解析失败,尝试提取 JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            # 如果仍然失败,返回原参数
            print(f"⚠️ [Guard] 无法解析 LLM 返回的 JSON: {response[:100]}")
            return args
    
    def validate_sync(
        self,
        tool_name: str,
        args: Dict[str, Any],
        schema: Dict[str, Any]
    ) -> Tuple[bool, List[ToolValidationError]]:
        """同步验证 (不进行自动修复)
        
        Args:
            tool_name: 工具名称
            args: 参数
            schema: Schema
            
        Returns:
            (是否有效, 错误列表)
        """
        is_valid, errors = self._validate_with_pydantic(args, schema)
        
        # 填充 tool_name
        for error in errors:
            error.tool_name = tool_name
        
        return is_valid, errors
