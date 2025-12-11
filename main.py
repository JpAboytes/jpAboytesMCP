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


@mcp.tool()
async def store_document(content: str, chunk_size: int = 500, chunk_overlap: int = 50) -> str:
    """
    Almacena un documento dividiéndolo en chunks óptimos para RAG y generando embeddings.
    
    Args:
        content: Contenido del documento a almacenar
        chunk_size: Tamaño máximo de cada chunk en caracteres (default: 500)
        chunk_overlap: Superposición entre chunks para mantener contexto (default: 50)
    
    Returns:
        Resultado de la operación con los IDs de los chunks creados
    """
    try:
        # Dividir el contenido en chunks
        chunks = _split_into_chunks(content, chunk_size, chunk_overlap)
        
        stored_chunks = []
        errors = []
        
        # Procesar cada chunk
        for i, chunk in enumerate(chunks, 1):
            try:
                # Generar embedding del chunk
                embedding = await gemini_client.generate_embedding(chunk)
                
                # Almacenar en la base de datos
                result = await supabase_client.store_embedding(chunk, embedding)
                
                if result['success']:
                    stored_chunks.append({
                        'chunk_id': i,
                        'doc_id': result['id'],
                        'size': len(chunk)
                    })
                else:
                    errors.append(f"Chunk {i}: {result['message']}")
                    
            except Exception as e:
                errors.append(f"Chunk {i}: {str(e)}")
        
        # Formatear resultado
        if stored_chunks:
            result = f" Documento almacenado exitosamente\n"
            result += f" Total de chunks: {len(chunks)}\n"
            result += f" Chunks almacenados: {len(stored_chunks)}\n"
            if errors:
                result += f"❌ Errores: {len(errors)}\n"
            result += f"\n Detalles:\n"
            for chunk_info in stored_chunks[:5]:  # Mostrar primeros 5
                result += f"   - Chunk {chunk_info['chunk_id']}: ID {chunk_info['doc_id']} ({chunk_info['size']} chars)\n"
            if len(stored_chunks) > 5:
                result += f"   ... y {len(stored_chunks) - 5} chunks más\n"
            
            if errors:
                result += f"\n Errores encontrados:\n"
                for error in errors[:3]:
                    result += f"   - {error}\n"
            
            return result
        else:
            return f" No se pudo almacenar ningún chunk. Errores: {'; '.join(errors)}"
        
    except Exception as e:
        return f" Error: {str(e)}"


def _split_into_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Divide un texto en chunks con superposición.
    
    Args:
        text: Texto a dividir
        chunk_size: Tamaño máximo de cada chunk
        overlap: Superposición entre chunks
        
    Returns:
        Lista de chunks de texto
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Si no es el último chunk, buscar el último punto o salto de línea
        if end < len(text):
            # Buscar el último separador natural (punto, salto de línea, etc.)
            last_period = text.rfind('.', start, end)
            last_newline = text.rfind('\n', start, end)
            last_separator = max(last_period, last_newline)
            
            if last_separator > start + chunk_size // 2:
                end = last_separator + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Mover el inicio con overlap
        start = end - overlap if end < len(text) else end
    
    return chunks
