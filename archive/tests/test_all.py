"""
Phase 5 功能综合测试脚本

一次性测试所有导出功能
"""

import sys
from pathlib import Path

print("="*70)
print("🚀 Agent Zero Phase 5 功能综合测试")
print("="*70)

# 测试 1: Dify 导出
print("\n" + "="*70)
print("测试 1/3: Dify YAML 导出")
print("="*70)
try:
    exec(open("test_dify.py", encoding="utf-8").read())
    print("✅ Dify 导出测试通过")
except Exception as e:
    print(f"❌ Dify 导出测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 2: ZIP 导出
print("\n" + "="*70)
print("测试 2/3: ZIP 打包导出")
print("="*70)
try:
    exec(open("test_zip.py", encoding="utf-8").read())
    print("✅ ZIP 导出测试通过")
except Exception as e:
    print(f"❌ ZIP 导出测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试 3: README 生成
print("\n" + "="*70)
print("测试 3/3: README 自动生成")
print("="*70)
try:
    exec(open("test_readme.py", encoding="utf-8").read())
    print("✅ README 生成测试通过")
except Exception as e:
    print(f"❌ README 生成测试失败: {e}")
    import traceback
    traceback.print_exc()

# 总结
print("\n" + "="*70)
print("🎉 Phase 5 功能测试完成")
print("="*70)

print("\n📊 生成的文件:")
files = [
    "test_dify_export.yml",
    "test_export.zip",
    "TEST_README.md"
]

for file in files:
    file_path = Path(file)
    if file_path.exists():
        size = file_path.stat().st_size
        print(f"   ✅ {file} ({size:,} 字节)")
    else:
        print(f"   ❌ {file} (未生成)")

print("\n💡 下一步:")
print("   1. 查看生成的文件")
print("   2. 将 test_dify_export.yml 导入到 Dify 测试")
print("   3. 解压 test_export.zip 查看内容")
print("   4. 阅读 TEST_README.md")

print("\n" + "="*70)
