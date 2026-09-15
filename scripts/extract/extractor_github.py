"""
Extractor de la API de GitHub.
Obtiene los repositorios de tecnología más populares (por estrellas) 
en lenguajes clave para analizar la demanda del mercado tech.
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
from utils.config import Config
from utils.logger import setup_logger
from utils.api_client import APIClient


class GitHubExtractor:
    """
    Extrae datos de repositorios populares de GitHub usando la API REST.
    """
    
    # Lenguajes clave para analizar la demanda del mercado tech
    TARGET_LANGUAGES = ["Python", "JavaScript", "TypeScript", "Rust", "Go"]
    
    def __init__(self):
        """Inicializa el extractor."""
        self.logger = setup_logger()
        self.config = Config()
        
        # Validar que el token esté configurado
        try:
            self.config.validate_credentials()
        except ValueError as e:
            self.logger.error(str(e))
            raise
        
        # Configurar cliente API con autenticación
        headers = {
            "Authorization": f"token {self.config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.client = APIClient(self.config.GITHUB_API_BASE_URL, headers=headers)
        self.output_path = self.config.DATA_RAW_PATH / "github_top_repos.json"
    
    def fetch_top_repos_by_language(self, language: str, per_page: int = 50) -> list:
        """
        Obtiene los repositorios más populares de un lenguaje específico.
        
        Args:
            language: Lenguaje de programación a buscar
            per_page: Número de repositorios a obtener (máx 100 por página)
            
        Returns:
            list: Lista de diccionarios con la información de los repositorios
        """
        self.logger.info(f"Buscando top {per_page} repositorios de {language}...")
        
        # Query de búsqueda: lenguaje + mínimo 5000 estrellas + ordenado por estrellas
        query = f"language:{language} stars:>5000"
        params = {
            "q": query,
            "sort": "stars",
            "order": "desc",
            "per_page": per_page
        }
        
        response = self.client.get("/search/repositories", params=params)
        
        if response and "items" in response:
            repos = response["items"]
            self.logger.info(f"✓ Encontrados {len(repos)} repositorios de {language}")
            return repos
        else:
            self.logger.warning(f"✗ No se encontraron repositorios para {language} o error en la API")
            return []
    
    def extract_all(self) -> pd.DataFrame:
        """
        Ejecuta la extracción para todos los lenguajes objetivo.
        
        Returns:
            pd.DataFrame: DataFrame con todos los repositorios extraídos
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO EXTRACCIÓN: GitHub Top Repositories API")
        self.logger.info("=" * 60)
        
        all_repos = []
        
        for lang in self.TARGET_LANGUAGES:
            repos = self.fetch_top_repos_by_language(lang, per_page=50)
            
            # Normalizar los datos para el DataFrame
            for repo in repos:
                normalized_repo = {
                    "language": lang,
                    "repo_name": repo.get("full_name"),
                    "description": repo.get("description", "No description"),
                    "stars": repo.get("stargazers_count", 0),
                    "forks": repo.get("forks_count", 0),
                    "watchers": repo.get("watchers_count", 0),
                    "open_issues": repo.get("open_issues_count", 0),
                    "created_at": repo.get("created_at"),
                    "updated_at": repo.get("updated_at"),
                    "topics": ", ".join(repo.get("topics", [])[:5])  # Top 5 topics
                }
                all_repos.append(normalized_repo)
        
        # Guardar datos crudos en JSON
        self.logger.info(f"Guardando datos crudos en: {self.output_path}")
        with open(self.output_path, 'w', encoding='utf-8') as f:
            json.dump(all_repos, f, indent=4, ensure_ascii=False)
        
        # Convertir a DataFrame
        df = pd.DataFrame(all_repos)
        self.logger.info(f"✓ Datos convertidos a DataFrame: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        return df
    
    def close(self):
        """Cierra la conexión del cliente API."""
        self.client.close()


def main():
    """Función principal para ejecutar el extractor."""
    extractor = GitHubExtractor()
    
    try:
        # Ejecutar extracción
        df = extractor.extract_all()
        
        print("\n" + "=" * 60)
        print("✓ EXTRACCIÓN DE GITHUB COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print(f"Archivo JSON guardado en: {extractor.output_path}")
        print(f"Filas totales: {df.shape[0]}")
        print(f"Columnas: {list(df.columns)}")
        print("=" * 60)
        
        # Mostrar un resumen rápido
        print("\nResumen de repositorios por lenguaje:")
        print(df.groupby('language').size().to_string())
        
    except Exception as e:
        print(f"\n✗ ERROR DURANTE LA EXTRACCIÓN: {e}")
    finally:
        extractor.close()


if __name__ == "__main__":
    main()