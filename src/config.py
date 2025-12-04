"""
Configuración para el servidor 
"""
import os
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    
    PORT: int = int(os.getenv('PORT', '8000'))
    NODE_ENV: str = os.getenv('NODE_ENV', 'development')
    
    SUPABASE_URL: str = os.getenv('SUPABASE_URL', '')
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '') or os.getenv('SUPABASE_KEY', '')
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    GEMINI_MODEL: str = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')
    GEMINI_EMBED_MODEL: str = os.getenv('GEMINI_EMBED_MODEL', 'models/text-embedding-004')
    
    # Configuración de embeddings y RAG
    EMBED_DIM: int = int(os.getenv('EMBED_DIM', '768'))
    SIMILARITY_THRESHOLD: float = float(os.getenv('SIMILARITY_THRESHOLD', '0.6'))
    TOPK_DOCUMENTS: int = int(os.getenv('TOPK_DOCUMENTS', '6'))
    
    @classmethod
    def validate_required_vars(cls) -> None:
        """Validar que las variables requeridas estén configuradas"""
        required_vars = [
            'SUPABASE_URL',
            'SUPABASE_SERVICE_ROLE_KEY', 
            'GEMINI_API_KEY'
        ]
        
        missing_vars = []
        for var_name in required_vars:
            if not getattr(cls, var_name):
                missing_vars.append(var_name)
        
        if missing_vars:
            print("❌ Faltan las siguientes variables de entorno:")
            for var in missing_vars:
                print(f"   - {var}")
            
            if cls.NODE_ENV == 'production':
                print("⚠️  Continuando en modo producción - algunas funciones pueden fallar")
                return
            else:
                raise ValueError(f"Variables de entorno faltantes: {', '.join(missing_vars)}")
        
        print("✅ Configuración cargada correctamente")

# Instancia global de configuración
config = Config()

# NO validar automáticamente en import para evitar errores de startup
# La validación se hará cuando se use el cliente
