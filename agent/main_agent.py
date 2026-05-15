"""
Agent 主类实现
Main Agent Class Implementation
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from agent.config import Config, get_logger
from agent.tools import ToolFactory


logger = get_logger(__name__)


class MedicalLiteratureAgent:
    """肾内科医学文献智能Agent"""
    
    def __init__(self, config: Optional[Config] = None):
        """初始化Agent"""
        self.config = config or Config()
        self.search_history: List[Dict[str, Any]] = []
        self.tools = {}
        self._init_tools()
        logger.info("MedicalLiteratureAgent initialized")
    
    def _init_tools(self):
        """初始化工具"""
        available_tools = ToolFactory.get_available_tools()
        for tool_name in available_tools:
            tool = ToolFactory.create_tool(tool_name)
            if tool:
                self.tools[tool_name] = tool
                logger.info(f"Tool loaded: {tool_name}")
    
    def search_literature(self, query: str, source: str = "pubmed", limit: int = 10) -> Dict[str, Any]:
        """
        搜索文献
        
        Args:
            query: 搜索关键词
            source: 数据库源
            limit: 返回结果数量
        
        Returns:
            搜索结果
        """
        logger.info(f"Searching literature: query={query}, source={source}")
        
        tool = self.tools.get("literature_search")
        if not tool:
            return {"error": "Literature search tool not available"}
        
        result = tool.execute(query=query, source=source, limit=limit)
        self._record_search("search_literature", {"query": query, "source": source, "limit": limit})
        
        return result
    
    def get_guideline(self, guideline: str = "kdigo", topic: str = "") -> Dict[str, Any]:
        """
        查询医学指南
        
        Args:
            guideline: 指南类型
            topic: 主题
        
        Returns:
            指南信息
        """
        logger.info(f"Getting guideline: guideline={guideline}, topic={topic}")
        
        tool = self.tools.get("guidelines")
        if not tool:
            return {"error": "Guidelines tool not available"}
        
        result = tool.execute(guideline=guideline, topic=topic)
        self._record_search("get_guideline", {"guideline": guideline, "topic": topic})
        
        return result
    
    def translate_text(self, text: str, target_lang: str = "zh-CN") -> Dict[str, Any]:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            target_lang: 目标语言
        
        Returns:
            翻译结果
        """
        logger.info(f"Translating text: target_lang={target_lang}")
        
        tool = self.tools.get("translation")
        if not tool:
            return {"error": "Translation tool not available"}
        
        result = tool.execute(text=text, target_lang=target_lang)
        self._record_search("translate_text", {"text_length": len(text), "target_lang": target_lang})
        
        return result
    
    def extract_data(self, paper_id: str, extraction_type: str = "abstract") -> Dict[str, Any]:
        """
        提取数据
        
        Args:
            paper_id: 论文ID
            extraction_type: 提取类型
        
        Returns:
            提取结果
        """
        logger.info(f"Extracting data: paper_id={paper_id}, type={extraction_type}")
        
        tool = self.tools.get("data_extraction")
        if not tool:
            return {"error": "Data extraction tool not available"}
        
        result = tool.execute(paper_id=paper_id, extraction_type=extraction_type)
        self._record_search("extract_data", {"paper_id": paper_id, "extraction_type": extraction_type})
        
        return result
    
    def query_database(self, database: str, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        查询公共数据库
        
        Args:
            database: 数据库名称
            query: 搜索查询
            limit: 返回结果数量
        
        Returns:
            查询结果
        """
        logger.info(f"Querying database: database={database}, query={query}")
        
        tool = self.tools.get("database")
        if not tool:
            return {"error": "Database tool not available"}
        
        result = tool.execute(database=database, query=query, limit=limit)
        self._record_search("query_database", {"database": database, "query": query, "limit": limit})
        
        return result
    
    def comprehensive_search(self, query: str) -> Dict[str, Any]:
        """
        综合搜索
        
        Args:
            query: 搜索关键词
        
        Returns:
            综合搜索结果
        """
        logger.info(f"Comprehensive search: query={query}")
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "results": {}
        }
        
        # 执行多个搜索
        results["results"]["literature_pubmed"] = self.search_literature(query, "pubmed", 5)
        results["results"]["guidelines"] = self.get_guideline("kdigo", query)
        results["results"]["database_geo"] = self.query_database("geo", query, 5)
        
        self._record_search("comprehensive_search", {"query": query})
        
        return results
    
    def _record_search(self, action: str, params: Dict[str, Any]):
        """记录搜索历史"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "params": params
        }
        self.search_history.append(record)
        logger.debug(f"Search recorded: {action}")
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """获取搜索历史"""
        return self.search_history
    
    def clear_history(self):
        """清除搜索历史"""
        self.search_history.clear()
        logger.info("Search history cleared")
    
    def print_info(self):
        """打印系统信息"""
        print("\n" + "="*70)
        print("ℹ️  系统信息 (System Information)")
        print("="*70)
        
        print("\n📋 配置信息:")
        config_dict = Config.get_all()
        for key, value in config_dict.items():
            print(f"  {key}: {value}")
        
        print("\n🛠️  可用工具:")
        for tool_name, tool in self.tools.items():
            print(f"  ✓ {tool_name}: {tool.description}")
        
        print("\n📊 搜索历史统计:")
        print(f"  总搜索数: {len(self.search_history)}")
        if self.search_history:
            action_counts = {}
            for record in self.search_history:
                action = record['action']
                action_counts[action] = action_counts.get(action, 0) + 1
            
            for action, count in action_counts.items():
                print(f"  {action}: {count}")
        
        print("\n" + "="*70)
