"""
Extractor de la API de RemoteOK.
Obtiene ofertas de empleo tech remoto en tiempo real, 
incluyendo salarios, roles, ubicación y tecnologías requeridas.
"""

# ============================================
# CONFIGURACIÓN DE PATHS (IMPORTANTE)
# ============================================
import sys
from pathlib import Path

scripts_path = Path(__file__).parent.parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# ============================================
# IMPORTS DEL PROYECTO
# ============================================
import json
import pandas as pd
import requests
from datetime import datetime
from utils.config import Config
from utils.logger import setup_logger
from utils.api_client import APIClient


class RemoteOKExtractor:
    """
    Extrae ofertas de empleo tech remoto desde la API pública de RemoteOK.
    No requiere autenticación.
    """
    
    # URL de la API pública de RemoteOK
    API_URL = "https://remoteok.com/api"
    
    # Tags tecnológicos clave para filtrar ofertas relevantes
    TECH_TAGS = [
        "python", "javascript", "typescript", "java", "rust", "go",
        "react", "vue", "angular", "node", "django", "flask", "fastapi",
        "sql", "postgresql", "mongodb", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "data", "machine-learning", "ai",
        "devops", "backend", "frontend", "full-stack", "mobile", "ios", "android"
    ]
    
    def __init__(self):
        """Inicializa el extractor."""
        self.logger = setup_logger()
        self.config = Config()
        self.client = APIClient(self.API_URL)
        self.output_path = self.config.DATA_RAW_PATH / "remoteok_jobs.json"
    
    def fetch_jobs(self) -> list:
        """
        Obtiene todas las ofertas de empleo de RemoteOK.
        
        Returns:
            list: Lista de ofertas de empleo
        """
        self.logger.info(f"Conectando con la API de RemoteOK: {self.API_URL}")
        
        # Headers para simular un navegador real (evita bloqueos)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.client.session.headers.update(headers)
        
        response = self.client.get("")
        
        if not response:
            self.logger.error("✗ No se pudo conectar con la API de RemoteOK")
            return []
        
        # La API devuelve un array donde el primer elemento es metadata
        # y los siguientes son las ofertas de empleo
        if isinstance(response, list) and len(response) > 1:
            jobs = response[1:]  # Saltar el elemento de metadata
            self.logger.info(f"✓ Obtenidas {len(jobs)} ofertas de empleo totales")
            return jobs
        else:
            self.logger.warning("✗ Formato de respuesta inesperado")
            return []
    
    def is_tech_job(self, job: dict) -> bool:
        """
        Determina si una oferta es del sector tech basándose en sus tags.
        
        Args:
            job: Diccionario con la oferta de empleo
            
        Returns:
            bool: True si es una oferta tech
        """
        tags = job.get("tags", [])
        if not tags:
            return False
        
        tags_lower = [tag.lower() for tag in tags]
        return any(tag in tags_lower for tag in self.TECH_TAGS)
    
    def normalize_job(self, job: dict) -> dict:
        """
        Normaliza una oferta de empleo para el DataFrame.
        
        Args:
            job: Oferta de empleo cruda
            
        Returns:
            dict: Oferta normalizada
        """
        # Procesar rango salarial si existe
        salary_min = job.get("salary_min")
        salary_max = job.get("salary_max")
        salary_currency = job.get("salary_currency", "USD")
        
        if salary_min and salary_max:
            salary_avg = (salary_min + salary_max) / 2
        else:
            salary_avg = None
        
        return {
            "id": job.get("id"),
            "job_title": job.get("position", "No title"),
            "company": job.get("company", "Unknown"),
            "description": job.get("description", "")[:500],  # Truncar a 500 caracteres
            "location": job.get("location", "Remote"),
            "tags": ", ".join(job.get("tags", [])[:10]),  # Top 10 tags
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_avg": salary_avg,
            "salary_currency": salary_currency,
            "posted_at": job.get("date"),
            "url": job.get("url"),
            "logo": job.get("logo")
        }
    
    def extract_all(self) -> pd.DataFrame:
        """
        Ejecuta la extracción completa de ofertas tech.
        
        Returns:
            pd.DataFrame: DataFrame con ofertas tech normalizadas
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO EXTRACCIÓN: RemoteOK Jobs API (Tiempo Real)")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info("=" * 60)
        
        # Obtener todas las ofertas
        all_jobs = self.fetch_jobs()
        
        if not all_jobs:
            self.logger.warning("No se obtuvieron ofertas. Abortando.")
            return pd.DataFrame()
        
        # Filtrar solo ofertas tech
        tech_jobs = [job for job in all_jobs if self.is_tech_job(job)]
        self.logger.info(f"✓ Ofertas tech filtradas: {len(tech_jobs)} de {len(all_jobs)} totales")
        
        # Normalizar datos
        normalized_jobs = [self.normalize_job(job) for job in tech_jobs]
        
        # Guardar datos crudos en JSON
        self.logger.info(f"Guardando datos crudos en: {self.output_path}")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(normalized_jobs, f, indent=4, ensure_ascii=False)
        
        # Convertir a DataFrame
        df = pd.DataFrame(normalized_jobs)
        self.logger.info(f"✓ DataFrame creado: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        return df
    
    def close(self):
        """Cierra la conexión del cliente API."""
        self.client.close()


def main():
    """Función principal para ejecutar el extractor."""
    extractor = RemoteOKExtractor()
    
    try:
        # Ejecutar extracción
        df = extractor.extract_all()
        
        if not df.empty:
            print("\n" + "=" * 60)
            print("✓ EXTRACCIÓN DE REMOTEOK COMPLETADA EXITOSAMENTE")
            print("=" * 60)
            print(f"Archivo JSON guardado en: {extractor.output_path}")
            print(f"Ofertas tech obtenidas: {df.shape[0]}")
            print(f"Columnas: {list(df.columns)}")
            print("=" * 60)
            
            # Mostrar estadísticas rápidas
            print("\nEstadísticas salariales (USD):")
            salaries = df['salary_avg'].dropna()
            if not salaries.empty:
                print(f"  Salario promedio: ${salaries.mean():,.0f}")
                print(f"  Salario mínimo: ${salaries.min():,.0f}")
                print(f"  Salario máximo: ${salaries.max():,.0f}")
                print(f"  Ofertas con salario: {len(salaries)} de {len(df)}")
            else:
                print("  (No hay datos salariales disponibles)")
            
            print("\nTop 5 empresas con más ofertas tech:")
            print(df['company'].value_counts().head(5).to_string())
        else:
            print("\n✗ No se pudieron extraer ofertas tech")
        
    except Exception as e:
        print(f"\n✗ ERROR DURANTE LA EXTRACCIÓN: {e}")
        import traceback
        traceback.print_exc()
    finally:
        extractor.close()


if __name__ == "__main__":
    main()