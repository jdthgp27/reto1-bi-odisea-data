""""
Extractor del dataset de Data Science Salaries 2023.
Descarga el CSV desde un repositorio público de GitHub (sin necesidad de API keys).
Ideal para análisis de mercado laboral tech, salarios por rol, experiencia y ubicación.
"""

# ============================================
# CONFIGURACIÓN DE PATHS (IMPORTANTE)
# ============================================
import sys
from pathlib import Path

# Agregar la carpeta 'scripts' al path de Python para poder importar 'utils'
scripts_path = Path(__file__).parent.parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# ============================================
# IMPORTS DEL PROYECTO
# ============================================
import pandas as pd
from tqdm import tqdm
import requests
from utils.config import Config
from utils.logger import setup_logger


class SalariesExtractor:
    """
    Extrae el dataset de Data Science Salaries 2023.
    
    El dataset se descarga directamente desde un repositorio público de GitHub,
    evitando problemas de autenticación de Kaggle.
    """
    
    # URL pública y estable del dataset de salarios tech
    DATASET_URL = "https://raw.githubusercontent.com/arminnorouzi/sparkml/main/Data/ds_salaries.csv"
    
    def __init__(self):
        """Inicializa el extractor."""
        self.logger = setup_logger()
        self.config = Config()
        self.output_path = self.config.DATA_RAW_PATH / "ds_salaries_2023.csv"
    
    def download_dataset(self) -> pd.DataFrame:
        """
        Descarga el dataset de salarios tech.
        
        Returns:
            pd.DataFrame: DataFrame con los datos crudos
        """
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO EXTRACCIÓN: Data Science Salaries 2023")
        self.logger.info("=" * 60)
        
        try:
            # Verificar si el archivo ya existe
            if self.output_path.exists():
                self.logger.info(f"Dataset ya existe en: {self.output_path}")
                self.logger.info("Cargando desde archivo local...")
                df = pd.read_csv(self.output_path)
                self.logger.info(f"✓ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
                return df
            
            # Descargar el dataset
            self.logger.info(f"Descargando dataset desde: {self.DATASET_URL}")
            
            response = requests.get(self.DATASET_URL, stream=True, timeout=120)
            response.raise_for_status()
            
            # Obtener tamaño total para barra de progreso
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            
            self.logger.info(f"Tamaño del archivo: {total_size / (1024*1024):.2f} MB")
            
            # Descargar con barra de progreso
            with open(self.output_path, 'wb') as f:
                with tqdm(
                    total=total_size,
                    unit='iB',
                    unit_scale=True,
                    desc="Descargando"
                ) as pbar:
                    for data in response.iter_content(chunk_size=block_size):
                        size = f.write(data)
                        pbar.update(size)
            
            self.logger.info(f"✓ Dataset descargado en: {self.output_path}")
            
            # Cargar el CSV en un DataFrame
            self.logger.info("Cargando dataset en DataFrame...")
            df = pd.read_csv(self.output_path)
            
            self.logger.info(f"✓ Dataset cargado: {df.shape[0]} filas, {df.shape[1]} columnas")
            self.logger.info(f"✓ Columnas principales: {list(df.columns)}")
            
            return df
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error al descargar el dataset: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error inesperado: {e}")
            raise
    
    def get_basic_info(self, df: pd.DataFrame) -> dict:
        """
        Obtiene información básica del dataset.
        
        Args:
            df: DataFrame con los datos
            
        Returns:
            dict: Diccionario con información básica
        """
        info = {
            "filas": df.shape[0],
            "columnas": df.shape[1],
            "columnas_nombres": list(df.columns),
            "nulls_por_columna": df.isnull().sum().to_dict(),
            "tipos_datos": df.dtypes.value_counts().to_dict(),
            "memoria_uso_mb": df.memory_usage(deep=True).sum() / (1024 * 1024)
        }
        
        return info
    
    def save_info_report(self, df: pd.DataFrame):
        """
        Guarda un reporte básico del dataset en la carpeta external.
        
        Args:
            df: DataFrame con los datos
        """
        info = self.get_basic_info(df)
        
        report_path = self.config.DATA_EXTERNAL_PATH / "ds_salaries_info.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("REPORTE: Data Science Salaries 2023\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total de filas: {info['filas']}\n")
            f.write(f"Total de columnas: {info['columnas']}\n")
            f.write(f"Uso de memoria: {info['memoria_uso_mb']:.2f} MB\n\n")
            
            f.write("Nulos por columna:\n")
            f.write("-" * 60 + "\n")
            for col, nulls in info['nulls_por_columna'].items():
                if nulls > 0:
                    f.write(f"  {col}: {nulls} ({nulls/info['filas']*100:.1f}%)\n")
            
            f.write("\n\nTipos de datos:\n")
            f.write("-" * 60 + "\n")
            for dtype, count in info['tipos_datos'].items():
                f.write(f"  {dtype}: {count} columnas\n")
        
        self.logger.info(f"✓ Reporte guardado en: {report_path}")


def main():
    """Función principal para ejecutar el extractor."""
    extractor = SalariesExtractor()
    
    # Descargar dataset
    df = extractor.download_dataset()
    
    # Guardar reporte de información
    extractor.save_info_report(df)
    
    print("\n" + "=" * 60)
    print("✓ EXTRACCIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 60)
    print(f"Archivo guardado en: {extractor.output_path}")
    print(f"Filas: {df.shape[0]}")
    print(f"Columnas: {df.shape[1]}")
    print("=" * 60)
    
    return df


if __name__ == "__main__":
    main()