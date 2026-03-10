# jpAboytesMCP - FastMCP Server

Servidor MCP para búsqueda semántica usando Google Gemini y Supabase, listo para deploy en FastMCP Cloud.

## 🚀 Deploy a FastMCP Cloud

### 1. Instalar FastMCP CLI
```bash
pip install fastmcp
```

### 2. Autenticarse
```bash
fastmcp login
```

### 3. Deploy
```bash
fastmcp deploy
```

El comando automáticamente detecta tu servidor y lo sube a FastMCP Cloud.

## ⚙️ Configuración

Crea un archivo `.env` en la raíz del proyecto:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_SERVICE_ROLE_KEY=tu-service-role-key
GEMINI_API_KEY=tu-gemini-api-key
GEMINI_MODEL=gemini-2.5-flash
GEMINI_EMBED_MODEL=models/text-embedding-004
EMBED_DIM=768
SIMILARITY_THRESHOLD=0.6
TOPK_DOCUMENTS=6
```

## 🎯 Uso con Claude Desktop

Agrega a tu archivo de configuración de Claude Desktop:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fiscai-search": {
      "command": "python",
      "args": ["-m", "src.main"],
      "cwd": "C:\\Users\\TuUsuario\\path\\to\\jpAboytesMCP",
      "env": {
        "SUPABASE_URL": "https://tu-proyecto.supabase.co",
        "SUPABASE_SERVICE_ROLE_KEY": "tu-key",
        "GEMINI_API_KEY": "tu-key"
      }
    }
  }
}
```

## 🔧 Herramientas Disponibles

### `search_documents`
Busca documentos similares usando búsqueda semántica.

**Parámetros:**
- `query` (string, requerido): Consulta en lenguaje natural
- `limit` (number, opcional): Número máximo de resultados (default: 6)
- `threshold` (number, opcional): Umbral de similitud 0-1 (default: 0.6)

### `generate_embedding`
Genera un embedding vectorial para un texto.

**Parámetros:**
- `text` (string, requerido): Texto para generar embedding

## 🧪 Verificación

```bash
# Verificar que el servidor se importa correctamente
python -c "from src.main import app; print('✅ OK')"
```

## 📝 Estructura del Proyecto

```
jpAboytesMCP/
├── src/
│   ├── __init__.py
│   ├── main.py              # Servidor MCP
│   ├── config.py            # Configuración
│   ├── gemini.py            # Cliente Gemini
│   └── supabase_client.py   # Cliente Supabase
├── .env                     # Variables de entorno (no incluir en git)
├── .gitignore
├── pyproject.toml
└── README.md
```

## 🐛 Solución de Problemas

### Error: "cannot import name 'gemini_client'"
Asegúrate de que todas las dependencias estén instaladas:
```bash
uv sync
```

### Error: "GEMINI_API_KEY no está configurada"
Verifica que tu archivo `.env` existe y contiene las credenciales correctas.

### El servidor no inicia en Claude Desktop
1. Verifica las rutas en `claude_desktop_config.json`
2. Asegúrate de usar rutas absolutas
3. Reinicia Claude Desktop después de cambiar la configuración

## 📄 Licencia

MIT

## 👤 Autor

**Jp Aboytes**
- GitHub: [@JpAboytes](https://github.com/JpAboytes)
