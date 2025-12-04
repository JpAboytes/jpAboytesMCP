"""
Cliente para Google Gemini AI 
"""
import asyncio
from typing import List
import google.generativeai as genai
from .config import config

class GeminiClient:
    """Cliente para interactuar con Google Gemini AI"""
    
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY no está configurada")
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera embedding para un texto usando Gemini
        
        Args:
            text: Texto para generar embedding
            
        Returns:
            Lista de números representando el embedding
        """
        try:
            # Para gemini-embedding-001, no se especifica output_dimensionality
            # Este modelo produce embeddings de 768 dimensiones por defecto
            if 'gemini-embedding-001' in config.GEMINI_EMBED_MODEL:
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=config.GEMINI_EMBED_MODEL,
                    content=text,
                    task_type="RETRIEVAL_QUERY"
                )
            else:
                # Para text-embedding-004 y modelos más nuevos
                result = await asyncio.to_thread(
                    genai.embed_content,
                    model=config.GEMINI_EMBED_MODEL,
                    content=text,
                    task_type="RETRIEVAL_QUERY",
                    output_dimensionality=config.EMBED_DIM
                )
            
            # Extraer embedding según la estructura de respuesta
            if hasattr(result, 'embedding'):
                emb = result.embedding
                # Si es un dict con 'values'
                if isinstance(emb, dict) and 'values' in emb:
                    return emb['values']
                # Si tiene atributo values
                if hasattr(emb, 'values'):
                    return list(emb.values)
                # Si es una lista directamente
                if isinstance(emb, list):
                    return emb
            elif isinstance(result, dict) and 'embedding' in result:
                emb = result['embedding']
                if isinstance(emb, dict) and 'values' in emb:
                    return emb['values']
                if isinstance(emb, list):
                    return emb
            
            raise RuntimeError("No se pudo extraer embedding de la respuesta")
            
        except Exception as error:
            print(f"Error generando embedding: {error}")
            import traceback
            traceback.print_exc()
            raise error


# Instancia global del cliente - con manejo de errores
try:
    gemini_client = GeminiClient()
except Exception as e:
    print(f"⚠️  Warning: No se pudo crear cliente Gemini: {e}")
    gemini_client = None
