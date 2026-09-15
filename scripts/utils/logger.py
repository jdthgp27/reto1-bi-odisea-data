"""
Módulo de logging centralizado.
Configura el sistema de logs para todo el pipeline ETL.
"""

import sys
from loguru import logger
from .config import Config


def setup_logger():
    """
    Configura el sistema de logging con loguru.
    
    Returns:
        logger: Instancia de logger configurada
    """
    # Remover handler por defecto
    logger.remove()
    
    # Configurar formato de log
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Agregar handler para consola
    logger.add(
        sys.stderr,
        format=log_format,
        level=Config.LOG_LEVEL,
        colorize=True
    )
    
    # Agregar handler para archivo de log
    log_file = Config.PROJECT_ROOT / "logs" / "etl_pipeline.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        format=log_format,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip"
    )
    
    logger.info("Sistema de logging inicializado")
    logger.info(f"Nivel de log: {Config.LOG_LEVEL}")
    logger.info(f"Archivo de log: {log_file}")
    
    return logger