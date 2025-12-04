"""
Servidor FastMCP para búsqueda semántica con Gemini y Supabase
Entry point para FastMCP Cloud deployment
"""
import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastmcp import FastMCP
from src.gemini import gemini_client
from src.supabase_client import supabase_client
from src.config import config

# Crear servidor FastMCP
mcp = FastMCP("JpChatbotMCP")

@mcp.tool()
async def search_documents(
    query: str,
    limit: int = None,
    threshold: float = None
) -> str:
    """
    Busca documentos similares usando búsqueda semántica con Gemini embeddings y Supabase.
    
    Args:
        query: Consulta de búsqueda en lenguaje natural
        limit: Número máximo de documentos a retornar (default del config: 5)
        threshold: Umbral de similitud 0-1 (default del config: 0.7)
    
    Returns:
        Resultados de búsqueda formateados con documentos similares
    """
    # Usar valores por defecto del config si no se especifican
    if limit is None:
        limit = config.TOPK_DOCUMENTS
    if threshold is None:
        threshold = config.SIMILARITY_THRESHOLD
    
    try:
        # Generar embedding de la consulta
        embedding = await gemini_client.generate_embedding(query)
        
        # Buscar documentos similares
        documents = await supabase_client.search_similar_documents(
            embedding=embedding,
            limit=limit,
            threshold=threshold
        )
        
        if not documents:
            return "No se encontraron documentos similares para la consulta."
        
        # Formatear resultados
        result = f"📚 Encontrados {len(documents)} documentos similares:\n\n"
        for i, doc in enumerate(documents, 1):
            similarity = doc.get('similarity', 0)
            title = doc.get('title', 'Sin título')
            scope = doc.get('scope', 'N/A')
            content = doc.get('content', '')[:200] + '...'
            source = doc.get('source_url', 'N/A')
            
            result += f"{i}. **{title}** (Similitud: {similarity:.2%})\n"
            result += f"   - Ámbito: {scope}\n"
            result += f"   - Contenido: {content}\n"
            result += f"   - Fuente: {source}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error en la búsqueda: {str(e)}"


@mcp.tool()
async def generate_embedding(text: str) -> str:
    """
    Genera un embedding vectorial para un texto usando Gemini AI.
    
    Args:
        text: Texto para generar el embedding
    
    Returns:
        Información sobre el embedding generado (dimensiones y valores de muestra)
    """
    try:
        embedding = await gemini_client.generate_embedding(text)
        
        result = f"✅ Embedding generado exitosamente\n"
        result += f"- Dimensiones: {len(embedding)}\n"
        result += f"- Primeros 5 valores: {embedding[:5]}\n"
        result += f"- Últimos 5 valores: {embedding[-5:]}\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error generando embedding: {str(e)}"
