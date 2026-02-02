"""Tool Discovery Engine - Local tool search and discovery.

This module implements the tool discovery system that searches the local
tool index and returns matching tools based on user requirements.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import re

from ..schemas import ToolDefinition
from ..utils.debug_logger import debug_log


class ToolDiscoveryEngine:
    """工具发现引擎 - 本地索引搜索
    
    ToolDiscoveryEngine 负责:
    1. 加载本地工具索引
    2. 基于关键词搜索匹配工具
    3. 返回工具定义供后续使用
    """
    
    def __init__(self, index_path: Optional[Path] = None):
        """初始化工具发现引擎
        
        Args:
            index_path: 工具索引文件路径,默认为 src/tools/data/tools_index.json
        """
        if index_path is None:
            index_path = Path(__file__).parent.parent / "tools" / "data" / "tools_index.json"
        
        self.index_path = index_path
        self.tools = self._load_index()
    
    def _load_index(self) -> List[Dict[str, Any]]:
        """加载工具索引
        
        Returns:
            工具定义列表
        """
        if not self.index_path.exists():
            print(f"⚠️ [ToolDiscovery] 工具索引文件不存在: {self.index_path}")
            return []
        
        try:
            with open(self.index_path, 'r', encoding='utf-8') as f:
                tools = json.load(f)
            print(f"✅ [ToolDiscovery] 加载了 {len(tools)} 个工具")
            return tools
        except Exception as e:
            print(f"❌ [ToolDiscovery] 加载索引失败: {e}")
            return []
    
    def search(
        self, 
        query: str, 
        top_k: int = 3,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """本地搜索工具 (Token-based Fuzzy Matching)"""
        if not self.tools:
            return []
        
        # 0. Debug Log
        debug_log("ToolDiscovery", f"Searching for '{query}' (Category: {category})")
        
        # 关键词匹配评分
        query_lower = query.lower()
        
        scores = []
        for tool in self.tools:
            # 分类过滤
            if category and tool.get("category") != category:
                continue
            
            score = 0.0
            debug_hits = []
            
            # 1. 准备目标词 (Name Tokens + Aliases)
            # Split by non-alphanumeric/non-chinese
            tool_name_tokens = set(re.split(r'[^a-zA-Z0-9\u4e00-\u9fa5]+', tool["name"].lower()))
            target_tokens = {t for t in tool_name_tokens if t} # Filter empty
            
            if "aliases" in tool:
                for alias in tool["aliases"]:
                    target_tokens.add(alias.lower())
            
            # 2. 遍历匹配
            for token in target_tokens:
                if len(token) <= 1: 
                    continue 

                # Check containment
                if token in query_lower:
                    # 3. 权重分级
                    token_score = 0
                    if token in ["tavily", "arxiv", "notion", "google", "bing", "wolfram", "youtube", "serper"]: # Strong proper nouns
                        token_score = 15.0
                    elif token in ["search", "联网", "tool", "api", "find", "query", "news", "image", "code", "repl"]: # Functional keywords
                        token_score = 5.0
                    else:
                        token_score = 2.0
                    
                    score += token_score
                    debug_hits.append(f"{token}({token_score})")

            # 4. ID Match (Bonus)
            if tool["id"].lower() in query_lower:
                score += 10.0
                debug_hits.append(f"ID({10.0})")
                
            if score > 0:
                scores.append((tool, score))
                debug_log("ToolDiscovery", f"Using {tool['name']}: Score={score} Hits={debug_hits}")
        
        # 排序并返回 top_k
        scores.sort(key=lambda x: x[1], reverse=True)
        return [tool for tool, _ in scores[:top_k]]
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取工具定义
        
        Args:
            tool_id: 工具 ID
            
        Returns:
            工具定义,如果不存在返回 None
        """
        for tool in self.tools:
            if tool["id"] == tool_id:
                return tool
        return None
    
    def list_categories(self) -> List[str]:
        """列出所有分类
        
        Returns:
            分类列表
        """
        categories = set(tool.get("category", "general") for tool in self.tools)
        return sorted(list(categories))
    
    def list_all_tools(self) -> List[Dict[str, Any]]:
        """列出所有工具
        
        Returns:
            所有工具定义列表
        """
        return self.tools.copy()
    
    def get_free_tools(self) -> List[Dict[str, Any]]:
        """获取所有免费工具 (不需要 API Key)
        
        Returns:
            免费工具列表
        """
        return [tool for tool in self.tools if not tool.get("requires_api_key", False)]
    
    def search_by_category(self, category: str) -> List[Dict[str, Any]]:
        """按分类搜索工具
        
        Args:
            category: 分类名称
            
        Returns:
            该分类下的所有工具
        """
        return [tool for tool in self.tools if tool.get("category") == category]
