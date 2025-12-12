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
    
    async def store_embedding(
        self, 
        content: str, 
        embedding: List[float]
    ) -> Dict[str, Any]:
        """
        Almacena un documento con su embedding en la tabla jp_documents
        
        Args:
            content: Contenido del documento
            embedding: Vector de embedding (debe ser 768 dimensiones)
            
        Returns:
            Dict con el resultado: {'success': bool, 'id': int, 'message': str}
        """
        try:
            # Validar dimensiones del embedding
            if len(embedding) != 768:
                error_msg = f"El embedding debe tener 768 dimensiones, pero tiene {len(embedding)}"
                return {'success': False, 'id': None, 'message': error_msg}
            
            data = {
                'content': content,
                'embedding': embedding
            }
            
            response = await asyncio.to_thread(
                lambda: self.client.table('jp_documents').insert(data).execute()
            )
            
            if response.data and len(response.data) > 0:
                document_id = response.data[0].get('id')
                print(f"[SUPABASE] ✅ Documento almacenado con ID: {document_id}")
                return {
                    'success': True, 
                    'id': document_id, 
                    'message': 'Documento almacenado correctamente'
                }
            else:
                error_msg = "No se recibió respuesta de Supabase"
                print(f"[SUPABASE] ❌ {error_msg}")
                return {'success': False, 'id': None, 'message': error_msg}
                
        except Exception as error:
            error_msg = f"Excepción al almacenar documento: {str(error)}"
            print(f"[SUPABASE] ❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'id': None, 'message': error_msg}
    
    async def search_similar_documents(
        self, 
        embedding: List[float], 
        limit: int = 5,
        threshold: float = None
    ) -> List[Dict[str, Any]]:
        """
        Buscar documentos similares usando embeddings
        
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
            
            # Preparar payload - usar query_embedding como en el script que funciona
            payload = {
                'query_embedding': embedding,  # float8[] - igual que simulate_recomendation.py
                'match_threshold': threshold,
                'match_count': limit
            }
            
            # Usar match_documents (única función RPC disponible)
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