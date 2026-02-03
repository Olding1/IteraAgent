"""Tool index builder for IteraAgent v8.0.

This script generates the tools_index.json file from the curated tool definitions.
"""

import json
from pathlib import Path
from .definitions import CURATED_TOOLS


def build_index(output_path: Path = None) -> None:
    """生成 tools_index.json

    Args:
        output_path: 输出路径,默认为 src/tools/data/tools_index.json
    """
    if output_path is None:
        output_path = Path(__file__).parent / "data" / "tools_index.json"

    # 确保目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入 JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(CURATED_TOOLS, f, indent=2, ensure_ascii=False)

    print(f"✅ 工具索引已生成: {output_path}")
    print(f"📊 工具数量: {len(CURATED_TOOLS)}")

    # 统计信息
    categories = {}
    for tool in CURATED_TOOLS:
        cat = tool["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("\n📋 分类统计:")
    for cat, count in sorted(categories.items()):
        print(f"  - {cat}: {count} 个工具")

    # API Key 统计
    free_count = sum(1 for t in CURATED_TOOLS if not t["requires_api_key"])
    api_count = len(CURATED_TOOLS) - free_count
    print(f"\n🔑 API Key 统计:")
    print(f"  - 免费工具: {free_count}")
    print(f"  - 需要 API Key: {api_count}")


def validate_tool_definitions() -> bool:
    """验证工具定义的完整性

    Returns:
        是否所有工具定义都有效
    """
    print("🔍 验证工具定义...")

    required_fields = [
        "id",
        "name",
        "description",
        "package_name",
        "import_path",
        "category",
        "args_schema",
    ]

    all_valid = True
    for i, tool in enumerate(CURATED_TOOLS):
        # 检查必填字段
        for field in required_fields:
            if field not in tool:
                print(f"❌ 工具 #{i+1} 缺少字段: {field}")
                all_valid = False

        # 检查 args_schema 结构
        if "args_schema" in tool and tool["args_schema"]:
            schema = tool["args_schema"]
            if "type" not in schema or schema["type"] != "object":
                print(f"⚠️ 工具 {tool.get('id', f'#{i+1}')} 的 args_schema 应该是 object 类型")

            if "properties" not in schema:
                print(f"⚠️ 工具 {tool.get('id', f'#{i+1}')} 的 args_schema 缺少 properties")

        # 检查示例
        if "examples" in tool and tool["examples"]:
            for j, example in enumerate(tool["examples"]):
                if not isinstance(example, dict):
                    print(f"⚠️ 工具 {tool.get('id', f'#{i+1}')} 的示例 #{j+1} 应该是字典")

    if all_valid:
        print("✅ 所有工具定义验证通过")
    else:
        print("❌ 部分工具定义存在问题")

    return all_valid


if __name__ == "__main__":
    # 验证工具定义
    if validate_tool_definitions():
        # 生成索引
        build_index()
    else:
        print("\n⚠️ 请修复工具定义后再生成索引")
