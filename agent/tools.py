"""
Agent 工具集合模块
Tools Module for Medical Literature Agent
"""

import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseTool(ABC):
    """基础工具类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        pass


class LiteratureSearchTool(BaseTool):
    """文献搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="LiteratureSearch",
            description="Search medical literature from PubMed, CNKI, and other databases"
        )
    
    def execute(self, query: str, source: str = "pubmed", limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        执行文献搜索
        
        Args:
            query: 搜索关键词
            source: 数据库源 (pubmed, cnki, vip, wanfang)
            limit: 返回结果数量
        
        Returns:
            搜索结果字典
        """
        try:
            if source == "pubmed":
                return self._search_pubmed(query, limit)
            elif source == "cnki":
                return self._search_cnki(query, limit)
            else:
                return {"error": f"Unsupported source: {source}"}
        except Exception as e:
            return {"error": str(e)}
    
    def _search_pubmed(self, query: str, limit: int) -> Dict[str, Any]:
        """PubMed搜索实现"""
        return {
            "source": "pubmed",
            "query": query,
            "total": 0,
            "articles": [],
            "message": "PubMed search requires NCBI API key"
        }
    
    def _search_cnki(self, query: str, limit: int) -> Dict[str, Any]:
        """中国知网搜索实现"""
        return {
            "source": "cnki",
            "query": query,
            "total": 0,
            "articles": [],
            "message": "CNKI search implementation"
        }


class GuidelinesTool(BaseTool):
    """医学指南查询工具"""
    
    GUIDELINES_DB = {
        "kdigo": {
            "name": "KDIGO Guidelines",
            "url": "https://kdigo.org/",
            "topics": ["CKD", "GN", "AKI", "DN"]
        },
        "asn": {
            "name": "American Society of Nephrology",
            "url": "https://www.asn-online.org/",
            "topics": ["CKD", "AKI", "transplantation"]
        },
        "era-edta": {
            "name": "European Renal Association",
            "url": "https://www.era-edta.org/",
            "topics": ["CKD", "dialysis", "transplantation"]
        },
        "china": {
            "name": "China Nephrology Guidelines",
            "url": "http://www.cma.org.cn/",
            "topics": ["CKD", "GN", "AKI", "dialysis"]
        }
    }
    
    def __init__(self):
        super().__init__(
            name="Guidelines",
            description="Query medical guidelines (KDIGO, ASN, ERA-EDTA, China)"
        )
    
    def execute(self, guideline: str = "kdigo", topic: str = "", **kwargs) -> Dict[str, Any]:
        """
        查询医学指南
        
        Args:
            guideline: 指南类型 (kdigo, asn, era-edta, china)
            topic: 主题 (CKD, GN, AKI, etc.)
        
        Returns:
            指南信息字典
        """
        guideline = guideline.lower()
        
        if guideline not in self.GUIDELINES_DB:
            return {
                "error": f"Unknown guideline: {guideline}",
                "available": list(self.GUIDELINES_DB.keys())
            }
        
        guideline_info = self.GUIDELINES_DB[guideline]
        
        return {
            "guideline": guideline,
            "name": guideline_info["name"],
            "url": guideline_info["url"],
            "topics": guideline_info["topics"],
            "topic_search": topic,
            "message": f"Found guidelines for {guideline_info['name']}"
        }


class TranslationTool(BaseTool):
    """翻译工具"""
    
    def __init__(self):
        super().__init__(
            name="Translation",
            description="Translate medical texts between Chinese and English"
        )
    
    def execute(self, text: str, target_lang: str = "zh-CN", **kwargs) -> Dict[str, Any]:
        """
        翻译文本
        
        Args:
            text: 待翻译文本
            target_lang: 目标语言 (zh-CN, en-US)
        
        Returns:
            翻译结果字典
        """
        try:
            if not text or len(text) == 0:
                return {"error": "Empty text"}
            
            # 实际翻译需要调用翻译API
            # 这里是框架实现
            return {
                "original": text[:100] + "..." if len(text) > 100 else text,
                "target_lang": target_lang,
                "translated": "[Translation would be here]",
                "message": "Translation requires API configuration"
            }
        except Exception as e:
            return {"error": str(e)}


class DataExtractionTool(BaseTool):
    """数据提取工具"""
    
    def __init__(self):
        super().__init__(
            name="DataExtraction",
            description="Extract key data from medical literature"
        )
    
    def execute(self, paper_id: str, extraction_type: str = "abstract", **kwargs) -> Dict[str, Any]:
        """
        从文献中提取数据
        
        Args:
            paper_id: 论文ID
            extraction_type: 提取类型 (abstract, tables, findings, etc.)
        
        Returns:
            提取结果字典
        """
        return {
            "paper_id": paper_id,
            "extraction_type": extraction_type,
            "data": {},
            "message": f"Extracting {extraction_type} from paper {paper_id}"
        }


class DatabaseTool(BaseTool):
    """公共数据库查询工具"""
    
    DATABASES = {
        "geo": "Gene Expression Omnibus",
        "tcga": "The Cancer Genome Atlas",
        "clinicaltrials": "Clinical Trials Registry",
        "biorxiv": "BioRxiv Preprints",
        "medrxiv": "MedRxiv Preprints"
    }
    
    def __init__(self):
        super().__init__(
            name="Database",
            description="Query public databases (GEO, TCGA, ClinicalTrials, BioRxiv, MedRxiv)"
        )
    
    def execute(self, database: str, query: str, limit: int = 10, **kwargs) -> Dict[str, Any]:
        """
        查询公共数据库
        
        Args:
            database: 数据库名称
            query: 搜索查询
            limit: 返回结果数量
        
        Returns:
            查询结果字典
        """
        database = database.lower()
        
        if database not in self.DATABASES:
            return {
                "error": f"Unknown database: {database}",
                "available": list(self.DATABASES.keys())
            }
        
        return {
            "database": database,
            "database_name": self.DATABASES[database],
            "query": query,
            "limit": limit,
            "results": [],
            "total": 0,
            "message": f"Querying {self.DATABASES[database]}"
        }


# 工具工厂
class ToolFactory:
    """工具工厂类"""
    
    _tools = {
        "literature_search": LiteratureSearchTool,
        "guidelines": GuidelinesTool,
        "translation": TranslationTool,
        "data_extraction": DataExtractionTool,
        "database": DatabaseTool
    }
    
    @classmethod
    def create_tool(cls, tool_name: str) -> Optional[BaseTool]:
        """创建工具实例"""
        tool_class = cls._tools.get(tool_name.lower())
        if tool_class:
            return tool_class()
        return None
    
    @classmethod
    def get_available_tools(cls) -> List[str]:
        """获取可用工具列表"""
        return list(cls._tools.keys())
