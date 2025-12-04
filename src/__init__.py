"""
Jp Chatbot MCP Server - Servidor MCP para interactuar con mi about page
"""

__version__ = "1.0.0"
__author__ = "Jp"
__description__ = "Servidor MCP para aprender"

from .config import config

# Importaciones opcionales para evitar errores de startup
try:
    from .gemini import gemini_client
except Exception:
    gemini_client = None

try:
    from .supabase_client import supabase_client
except Exception:
    supabase_client = None

try:
    from .main import main
except Exception:
    main = None

__all__ = [
    "main",
    "config", 
    "gemini_client",
    "supabase_client"
]