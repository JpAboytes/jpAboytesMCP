"""
Cliente para Supabase - Base de datos y funciones
"""
import asyncio
from typing import List, Dict, Any, Optional
from supabase import create_client, Client
from .config import config

class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    def __init__(self):
        if not config.SUPABASE_URL or not config.SUPABASE_SERVICE_ROLE_KEY:
            raise ValueError("Faltan variables de entorno de Supabase")
        self.client: Client = create_client(
            config.SUPABASE_URL,
            config.SUPABASE_SERVICE_ROLE_KEY
        )
    
    async def search_similar_documents(
        self, 
        embedding: List[float], 
        limit: int = 5,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar documentos similares usando embeddings
        Compatible con match_fiscai_documents RPC
        
        Args:
            embedding: Vector de embedding para la búsqueda
            limit: Número máximo de documentos a retornar
            threshold: Umbral de similitud (default: 0.6)
            
        Returns:
            Lista de documentos similares con campos: title, scope, content, source_url, similarity
        """
        try:
            if threshold is None:
                threshold = config.SIMILARITY_THRESHOLD if hasattr(config, 'SIMILARITY_THRESHOLD') else 0.6
            
            print(f"[SUPABASE] Buscando documentos similares...")
            print(f"[SUPABASE] - Embedding dimension: {len(embedding)}")
            print(f"[SUPABASE] - Match threshold: {threshold}")
            print(f"[SUPABASE] - Match count: {limit}")
            
            # Preparar payload - usar query_embedding como en el script que funciona
            payload = {
                'query_embedding': embedding,  # float8[] - igual que simulate_recomendation.py
                'match_threshold': threshold,
                'match_count': limit
            }
            
            # Usar match_documents (única función RPC disponible)
            print("[SUPABASE] Llamando match_documents RPC...")
            response = await asyncio.to_thread(
                lambda: self.client.rpc('match_documents', payload).execute()
            )
            
            if response.data:
                print(f"[SUPABASE] ✅ Encontrados {len(response.data)} documentos (fallback)")
                return response.data
            
            print("[SUPABASE] ⚠️  No se encontraron documentos")
            return []
            
        except Exception as error:
            print(f"[SUPABASE] ❌ Error buscando documentos similares: {error}")
            import traceback
            traceback.print_exc()
            return []


# Instancia global del cliente - con manejo de errores
try:
    supabase_client = SupabaseClient()
except Exception as e:
    print(f"⚠️  Warning: No se pudo crear cliente Supabase: {e}")
    supabase_client = None