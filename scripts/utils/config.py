"""
Módulo de configuración centralizada.
Carga variables de entorno desde .env y proporciona rutas del proyecto.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Clase de configuración centralizada para el proyecto."""
    
    # Cargar variables de entorno desde .env
    load_dotenv()
    
    # ============================================
    # RUTAS DEL PROYECTO (Ajustadas a la estructura real sin prefijos numéricos)
    # ============================================
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    DATA_RAW_PATH = PROJECT_ROOT / "data" / "raw"
    DATA_PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"
    DATA_EXTERNAL_PATH = PROJECT_ROOT / "data" / "external"
    OUTPUTS_PATH = PROJECT_ROOT / "outputs"
    CHARTS_PATH = OUTPUTS_PATH / "charts"
    CSV_ANALYSIS_PATH = OUTPUTS_PATH / "csv_analysis"
    SCREENSHOTS_PATH = OUTPUTS_PATH / "screenshots"
    REPORTS_PATH = PROJECT_ROOT / "reports"
    DOCS_PATH = PROJECT_ROOT / "docs"
    
    # ============================================
    # CREDENCIALES DE APIs
    # ============================================
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME")
    KAGGLE_KEY = os.getenv("KAGGLE_KEY")
    
    # ============================================
    # CONFIGURACIÓN GENERAL
    # ============================================
    PROJECT_NAME = os.getenv("PROJECT_NAME", "reto1-bi-odisea-data")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # ============================================
    # CONFIGURACIÓN DE APIs
    # ============================================
    GITHUB_API_BASE_URL = "https://api.github.com"
    BLS_API_BASE_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
    
    # ============================================
    # CONFIGURACIÓN DE DATOS
    # ============================================
    STACK_OVERFLOW_DATASET_URL = "https://raw.githubusercontent.com/stackoverflow/developer-survey/main/survey_results_public.csv"
    
    @classmethod
    def validate_credentials(cls):
        """Valida que las credenciales necesarias estén configuradas de forma segura."""
        errors = []
        
        # Verificamos que exista y tenga una longitud mínima de un token real (sin exponer el token)
        if not cls.GITHUB_TOKEN or len(cls.GITHUB_TOKEN) < 10:
            errors.append("GITHUB_TOKEN no configurado o es inválido en el archivo .env")
        
        if errors:
            raise ValueError(f"Errores de configuración:\n" + "\n".join(errors))
        
        return True
    
    @classmethod
    def create_directories(cls):
        """Crea todas las carpetas necesarias si no existen."""
        directories = [
            cls.DATA_RAW_PATH,
            cls.DATA_PROCESSED_PATH,
            cls.DATA_EXTERNAL_PATH,
            cls.CHARTS_PATH,
            cls.CSV_ANALYSIS_PATH,
            cls.SCREENSHOTS_PATH,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)