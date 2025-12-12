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
    
@mcp.tool()
async def generate_response(query: str) -> str:
    """
    Herramienta para generar una respuesta basada en el query del usuario.
    Args:
        query: Pregunta o consulta del usuario
    Returns:
        Respuesta generada
    """
    
    context = await match_documents(query)
    
    PROMPT = f"""
    Eres un asistente especializado cuya única función es responder preguntas sobre el
    currículum, trayectoria profesional, educación, proyectos, experiencia laboral y habilidades
    de Juan Pablo Aboytes Dessens.

    Usa exclusivamente la información proporcionada en la base de conocimiento recuperada
    por el sistema RAG. Si la información no aparece en los documentos recuperados, responde
    claramente que no está disponible y no inventes datos.

    Instrucciones:
    - Responde de forma clara, precisa y profesional.
    - No generes información que no esté en la base de conocimiento.
    - No asumas, no completes detalles y no alucines.
    - Si el usuario hace una pregunta fuera del alcance del CV, responde que solo puedes
    explicar información relacionada con su currículum.
    - Si la consulta es ambigua, pide una aclaración.
    - Si la base de conocimiento recuperada no contiene datos relevantes, dilo explícitamente.

    Base de conocimiento recuperada:
    {context}

    Consulta del usuario:
    {query}

    Respuesta:
    """
    
    response = await gemini_client.generate_text(PROMPT)
        
    return response



async def match_documents(query : str) -> str:
    """
    Herramienta para a partir del query buscar informacion en la base de conocimientos.
    """
    
    query_embedding = await gemini_client.generate_embedding(query)
    
    if not query_embedding:
        print(" No se pudo generar el embedding")
        return
    
    results = await supabase_client.search_similar_documents(
        embedding=query_embedding,
        limit=5,
        threshold=0.5
    )
    
    return results
    

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
