#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测脚本：查找项目中残留的 Agent Zero 相关引用

用法：
    python scripts/check_rename.py
    python scripts/check_rename.py --include-archive  # 包含 archive 目录
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict


# 要检测的模式
PATTERNS = [
    r"Agent Zero",
    r"Agent_Zero",
    r"agent-zero",
    r"agent_zero",
    r"AgentZero(?!_RAG)",  # 排除 AgentZero_RAG_Assistant（已生成的案例）
]

# 要排除的目录
EXCLUDE_DIRS = [
    ".git",
    "__pycache__",
    "venv",
    "node_modules",
    ".venv",
    "agents",  # 已生成的 Agent 目录
    "exports",  # 导出目录
    "archive",  # 历史备份（默认排除）
    "temp_agent_fast",  # 临时测试
    ".chroma",
    "chroma_db",
]

# 要排除的文件扩展名
EXCLUDE_EXTENSIONS = [
    ".pyc",
    ".pyo",
    ".so",
    ".dll",
    ".exe",
    ".db",
    ".sqlite",
    ".sqlite3",
    ".log",
    ".tmp",
    ".bak",
]


class Colors:
    """终端颜色"""
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    ENDC = "\033[0m"


def should_skip_path(path: Path, include_archive: bool = False) -> bool:
    """判断是否应该跳过该路径"""
    path_str = str(path)
    
    # 检查是否在排除目录中
    for exclude_dir in EXCLUDE_DIRS:
        if exclude_dir == "archive" and include_archive:
            continue
        if f"{os.sep}{exclude_dir}{os.sep}" in path_str or path_str.endswith(exclude_dir):
            return True
    
    # 检查文件扩展名
    if path.suffix in EXCLUDE_EXTENSIONS:
        return True
    
    return False


def search_in_file(file_path: Path, patterns: List[str]) -> List[Tuple[int, str, str]]:
    """
    在文件中搜索模式
    
    返回：[(行号, 匹配的模式, 行内容), ...]
    """
    matches = []
    
    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line_num, line in enumerate(f, 1):
                for pattern in patterns:
                    if re.search(pattern, line):
                        matches.append((line_num, pattern, line.strip()))
    except Exception as e:
        # 跳过无法读取的文件
        pass
    
    return matches


def scan_directory(root_dir: Path, include_archive: bool = False) -> Dict[Path, List[Tuple[int, str, str]]]:
    """
    扫描目录中的所有文件
    
    返回：{文件路径: [(行号, 模式, 行内容), ...]}
    """
    results = {}
    
    for file_path in root_dir.rglob("*"):
        if not file_path.is_file():
            continue
        
        if should_skip_path(file_path, include_archive):
            continue
        
        matches = search_in_file(file_path, PATTERNS)
        if matches:
            results[file_path] = matches
    
    return results


def print_results(results: Dict[Path, List[Tuple[int, str, str]]], root_dir: Path):
    """打印检测结果"""
    if not results:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 检测完成：未发现残留引用！{Colors.ENDC}")
        print(f"{Colors.GREEN}所有文件都已成功重命名为 IteraAgent{Colors.ENDC}\n")
        return
    
    print(f"\n{Colors.RED}{Colors.BOLD}⚠️  发现 {len(results)} 个文件包含残留引用：{Colors.ENDC}\n")
    
    total_matches = 0
    
    for file_path, matches in sorted(results.items()):
        rel_path = file_path.relative_to(root_dir)
        print(f"{Colors.CYAN}{Colors.BOLD}{rel_path}{Colors.ENDC}")
        
        for line_num, pattern, line_content in matches:
            total_matches += 1
            # 高亮显示匹配的模式
            highlighted_line = re.sub(
                f"({pattern})",
                f"{Colors.RED}\\1{Colors.ENDC}",
                line_content
            )
            print(f"  {Colors.YELLOW}第 {line_num} 行:{Colors.ENDC} {highlighted_line}")
        
        print()
    
    print(f"{Colors.MAGENTA}总计：{len(results)} 个文件，{total_matches} 处匹配{Colors.ENDC}\n")


def print_summary(results: Dict[Path, List[Tuple[int, str, str]]]):
    """打印摘要统计"""
    if not results:
        return
    
    print(f"{Colors.BOLD}📊 按文件类型统计：{Colors.ENDC}\n")
    
    by_extension = {}
    for file_path in results.keys():
        ext = file_path.suffix or "(无扩展名)"
        by_extension[ext] = by_extension.get(ext, 0) + 1
    
    for ext, count in sorted(by_extension.items(), key=lambda x: -x[1]):
        print(f"  {ext:20s} {count:3d} 个文件")
    
    print()


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="检测项目中残留的 Agent Zero 相关引用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--include-archive",
        action="store_true",
        help="包含 archive 目录（默认排除）"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="显示详细信息"
    )
    
    args = parser.parse_args()
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent
    
    print(f"{Colors.BOLD}🔍 开始检测项目中的残留引用...{Colors.ENDC}\n")
    print(f"项目目录: {root_dir}")
    print(f"包含 archive: {'是' if args.include_archive else '否'}")
    print(f"\n检测模式: {', '.join(PATTERNS)}")
    print(f"排除目录: {', '.join(EXCLUDE_DIRS if not args.include_archive else [d for d in EXCLUDE_DIRS if d != 'archive'])}")
    print("\n" + "=" * 70 + "\n")
    
    # 扫描目录
    results = scan_directory(root_dir, args.include_archive)
    
    # 打印结果
    print_results(results, root_dir)
    
    # 打印统计
    if results:
        print_summary(results)
        
        print(f"{Colors.YELLOW}💡 建议：{Colors.ENDC}")
        print(f"  1. 检查上述文件是否需要修改")
        print(f"  2. 如果是 archive 目录的文件，可以忽略（历史备份）")
        print(f"  3. 如果是 agents 目录的文件，可以忽略（已生成的测试案例）")
        print(f"  4. 其他文件建议手动检查并修复\n")
        
        sys.exit(1)  # 发现残留，返回错误码
    else:
        sys.exit(0)  # 未发现残留，返回成功


if __name__ == "__main__":
    main()

