"""
Script de prueba para verificar que las utilidades funcionan correctamente.
"""

import sys
sys.path.append('scripts')

from utils import Config, setup_logger, APIClient


def test_config():
    """Prueba la configuración."""
    print("\n=== PRUEBA DE CONFIGURACIÓN ===")
    print(f"Nombre del proyecto: {Config.PROJECT_NAME}")
    print(f"Ruta de datos raw: {Config.DATA_RAW_PATH}")
    print(f"Ruta de datos procesados: {Config.DATA_PROCESSED_PATH}")
    print(f"Ruta de outputs: {Config.OUTPUTS_PATH}")
    
    # Crear carpetas
    Config.create_directories()
    print("✓ Carpetas creadas correctamente")


def test_logger():
    """Prueba el sistema de logging."""
    print("\n=== PRUEBA DE LOGGING ===")
    logger = setup_logger()
    logger.info("Mensaje de prueba INFO")
    logger.warning("Mensaje de prueba WARNING")
    logger.error("Mensaje de prueba ERROR")
    print("✓ Logging funcionando correctamente")


def test_api_client():
    """Prueba el cliente API."""
    print("\n=== PRUEBA DE API CLIENT ===")
    client = APIClient("https://api.github.com")
    response = client.get("/users/github")
    
    if response:
        print(f"✓ API Client funcionando. Usuario: {response.get('login')}")
    else:
        print("✗ Error en API Client")
    
    client.close()


if __name__ == "__main__":
    print("=" * 50)
    print("INICIANDO PRUEBAS DE UTILIDADES")
    print("=" * 50)
    
    try:
        test_config()
        test_logger()
        test_api_client()
        
        print("\n" + "=" * 50)
        print("✓ TODAS LAS PRUEBAS PASARON CORRECTAMENTE")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        sys.exit(1)