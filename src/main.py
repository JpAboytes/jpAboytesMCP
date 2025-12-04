"""
Servidor MCP para búsqueda semántica con Gemini y Supabase
"""
import asyncio
from typing import List, Dict, Any
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .gemini import gemini_client
from .supabase_client import supabase_client
from .config import config

# Crear servidor MCP
app = Server("fiscai-search-server")

@app.list_tools()
async def list_tools() -> List[Tool]:
    """Lista las herramientas disponibles"""
    return [
        Tool(
            name="search_documents",
            description="Busca documentos similares usando búsqueda semántica con Gemini embeddings y Supabase",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Consulta de búsqueda en lenguaje natural"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Número máximo de documentos a retornar (default: 6)",
                        "default": 6
                    },
                    "threshold": {
                        "type": "number",
                        "description": "Umbral de similitud 0-1 (default: 0.6)",
                        "default": 0.6
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="generate_embedding",
            description="Genera un embedding vectorial para un texto usando Gemini AI",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "Texto para generar el embedding"
                    }
                },
                "required": ["text"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Maneja las llamadas a las herramientas"""
    
    if name == "search_documents":
        query = arguments.get("query")
        limit = arguments.get("limit", config.TOPK_DOCUMENTS)
        threshold = arguments.get("threshold", config.SIMILARITY_THRESHOLD)
        
        if not query:
            return [TextContent(
                type="text",
                text="Error: Se requiere el parámetro 'query'"
            )]
        
        try:
            print(f"\n🔍 Buscando: '{query}'")
            
            # Generar embedding de la consulta
            print("📊 Generando embedding...")
            embedding = await gemini_client.generate_embedding(query)
            print(f"✅ Embedding generado ({len(embedding)} dimensiones)")
            
            # Buscar documentos similares
            print("🔎 Buscando documentos similares...")
            documents = await supabase_client.search_similar_documents(
                embedding=embedding,
                limit=limit,
                threshold=threshold
            )
            
            if not documents:
                return [TextContent(
                    type="text",
                    text="No se encontraron documentos similares para la consulta."
                )]
            
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
            
            print(f"✅ Búsqueda completada: {len(documents)} resultados")
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ Error en la búsqueda: {str(e)}"
            print(error_msg)
            return [TextContent(type="text", text=error_msg)]
    
    elif name == "generate_embedding":
        text = arguments.get("text")
        
        if not text:
            return [TextContent(
                type="text",
                text="Error: Se requiere el parámetro 'text'"
            )]
        
        try:
            print(f"📊 Generando embedding para texto ({len(text)} caracteres)...")
            embedding = await gemini_client.generate_embedding(text)
            
            result = f"✅ Embedding generado exitosamente\n"
            result += f"- Dimensiones: {len(embedding)}\n"
            result += f"- Primeros 5 valores: {embedding[:5]}\n"
            result += f"- Últimos 5 valores: {embedding[-5:]}\n"
            
            return [TextContent(type="text", text=result)]
            
        except Exception as e:
            error_msg = f"❌ Error generando embedding: {str(e)}"
            print(error_msg)
            return [TextContent(type="text", text=error_msg)]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Herramienta desconocida '{name}'"
        )]


async def main():
    """Punto de entrada principal del servidor MCP"""
    print("🚀 Iniciando servidor MCP FiscAI Search...")
    print(f"📍 Modelo Gemini: {config.GEMINI_MODEL}")
    print(f"📍 Dimensiones embedding: {config.EMBED_DIM}")
    print(f"📍 Umbral de similitud: {config.SIMILARITY_THRESHOLD}")
    print(f"📍 Top K documentos: {config.TOPK_DOCUMENTS}")
    print("=" * 50)
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
