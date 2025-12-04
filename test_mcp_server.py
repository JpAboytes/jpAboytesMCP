"""
Script de prueba para verificar que el servidor MCP responde correctamente
"""
import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def test_server():
    """Probar el servidor MCP"""
    print("🧪 Probando servidor MCP...")
    print("=" * 60)
    
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "src.main"],
        env=None
    )
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Inicializar
                await session.initialize()
                print("✅ Servidor inicializado correctamente")
                
                # Listar herramientas
                tools = await session.list_tools()
                print(f"\n📋 Herramientas disponibles: {len(tools.tools)}")
                for tool in tools.tools:
                    print(f"   - {tool.name}: {tool.description[:60]}...")
                
                print("\n" + "=" * 60)
                print("✅ SERVIDOR FUNCIONA CORRECTAMENTE")
                print("=" * 60)
                print("\n🚀 Listo para usar en Claude Desktop!")
                
    except Exception as e:
        print(f"\n❌ Error probando servidor: {e}")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Verifica que:")
        print("   1. Todas las dependencias estén instaladas (uv sync)")
        print("   2. El archivo .env tenga las credenciales correctas")
        print("   3. Python esté en el PATH")

if __name__ == "__main__":
    asyncio.run(test_server())
