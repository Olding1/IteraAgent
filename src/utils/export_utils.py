"""
导出工具

提供 Agent 的导出功能，包括 ZIP 打包
"""

import zipfile
import shutil
from pathlib import Path
from typing import List, Optional


class ExportUtils:
    """导出工具类"""

    # 需要排除的文件和目录
    EXCLUDE_PATTERNS = [
        '__pycache__',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.git',
        '.gitignore',
        'venv',
        '.venv',
        'env',
        '.env',
        '.trace',
        '.reports',
        '*.log',
        '.DS_Store',
        'Thumbs.db'
    ]

    @staticmethod
    def export_agent_to_zip(
        agent_path: Path,
        output_path: Path,
        exclude_patterns: Optional[List[str]] = None
    ) -> Path:
        """
        将 Agent 打包为 ZIP

        Args:
            agent_path: Agent 目录路径
            output_path: 输出 ZIP 文件路径
            exclude_patterns: 额外的排除模式（可选）

        Returns:
            输出 ZIP 文件路径
        """
        agent_path = Path(agent_path)
        output_path = Path(output_path)

        # 合并排除模式
        exclude = ExportUtils.EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude.extend(exclude_patterns)

        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建 ZIP 文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 遍历所有文件
            for file_path in agent_path.rglob('*'):
                if file_path.is_file():
                    # 检查是否应该排除
                    if ExportUtils._should_exclude(file_path, agent_path, exclude):
                        continue

                    # 计算相对路径
                    arcname = file_path.relative_to(agent_path.parent)

                    # 添加到 ZIP
                    zipf.write(file_path, arcname)

        return output_path

    @staticmethod
    def _should_exclude(file_path: Path, base_path: Path, exclude_patterns: List[str]) -> bool:
        """
        检查文件是否应该被排除

        Args:
            file_path: 文件路径
            base_path: 基础路径
            exclude_patterns: 排除模式列表

        Returns:
            是否应该排除
        """
        # 获取相对路径
        try:
            rel_path = file_path.relative_to(base_path)
        except ValueError:
            return False

        # 检查每个部分
        for part in rel_path.parts:
            for pattern in exclude_patterns:
                # 简单的模式匹配
                if pattern.startswith('*'):
                    # 后缀匹配
                    if part.endswith(pattern[1:]):
                        return True
                elif pattern.endswith('*'):
                    # 前缀匹配
                    if part.startswith(pattern[:-1]):
                        return True
                else:
                    # 精确匹配
                    if part == pattern:
                        return True

        return False

    @staticmethod
    def export_agent_directory(
        agent_path: Path,
        output_dir: Path,
        exclude_patterns: Optional[List[str]] = None
    ) -> Path:
        """
        将 Agent 复制到指定目录

        Args:
            agent_path: Agent 目录路径
            output_dir: 输出目录路径
            exclude_patterns: 额外的排除模式（可选）

        Returns:
            输出目录路径
        """
        agent_path = Path(agent_path)
        output_dir = Path(output_dir)

        # 合并排除模式
        exclude = ExportUtils.EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude.extend(exclude_patterns)

        # 创建输出目录
        output_agent_dir = output_dir / agent_path.name
        output_agent_dir.mkdir(parents=True, exist_ok=True)

        # 复制文件
        for file_path in agent_path.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                if ExportUtils._should_exclude(file_path, agent_path, exclude):
                    continue

                # 计算目标路径
                rel_path = file_path.relative_to(agent_path)
                target_path = output_agent_dir / rel_path

                # 创建目标目录
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                shutil.copy2(file_path, target_path)

        return output_agent_dir

    @staticmethod
    def get_export_size(agent_path: Path, exclude_patterns: Optional[List[str]] = None) -> int:
        """
        计算导出文件的大小

        Args:
            agent_path: Agent 目录路径
            exclude_patterns: 额外的排除模式（可选）

        Returns:
            文件大小（字节）
        """
        agent_path = Path(agent_path)

        # 合并排除模式
        exclude = ExportUtils.EXCLUDE_PATTERNS.copy()
        if exclude_patterns:
            exclude.extend(exclude_patterns)

        total_size = 0

        # 遍历所有文件
        for file_path in agent_path.rglob('*'):
            if file_path.is_file():
                # 检查是否应该排除
                if ExportUtils._should_exclude(file_path, agent_path, exclude):
                    continue

                total_size += file_path.stat().st_size

        return total_size

    @staticmethod
    def format_size(size_bytes: int) -> str:
        """
        格式化文件大小

        Args:
            size_bytes: 字节数

        Returns:
            格式化后的字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


# 便捷函数
def export_to_zip(agent_path: Path, output_path: Path) -> Path:
    """
    将 Agent 导出为 ZIP

    Args:
        agent_path: Agent 目录路径
        output_path: 输出 ZIP 文件路径

    Returns:
        输出 ZIP 文件路径
    """
    return ExportUtils.export_agent_to_zip(agent_path, output_path)


def export_to_directory(agent_path: Path, output_dir: Path) -> Path:
    """
    将 Agent 导出到目录

    Args:
        agent_path: Agent 目录路径
        output_dir: 输出目录路径

    Returns:
        输出目录路径
    """
    return ExportUtils.export_agent_directory(agent_path, output_dir)


def get_agent_size(agent_path: Path) -> str:
    """
    获取 Agent 大小（格式化）

    Args:
        agent_path: Agent 目录路径

    Returns:
        格式化的大小字符串
    """
    size_bytes = ExportUtils.get_export_size(agent_path)
    return ExportUtils.format_size(size_bytes)
