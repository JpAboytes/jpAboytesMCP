"""
Entry point para FastMCP Cloud deployment
"""
from src.main import mcp

# El servidor se exporta directamente para FastMCP Cloud
__all__ = ['mcp']
