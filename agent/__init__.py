"""
Agent 包初始化模块
Package Initialization
"""

from agent.config import get_config, Config
from agent.tools import (
    BaseTool,
    LiteratureSearchTool,
    GuidelinesTool,
    TranslationTool,
    DataExtractionTool,
    DatabaseTool,
    ToolFactory
)
from agent.main_agent import MedicalLiteratureAgent

__all__ = [
    "get_config",
    "Config",
    "BaseTool",
    "LiteratureSearchTool",
    "GuidelinesTool",
    "TranslationTool",
    "DataExtractionTool",
    "DatabaseTool",
    "ToolFactory",
    "MedicalLiteratureAgent"
]

__version__ = "1.0.0"
__author__ = "Medical Literature Agent Team"
