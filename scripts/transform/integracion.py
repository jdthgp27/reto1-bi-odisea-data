"""
Script de Integración y Transformación de Datos.
Fusiona las 3 fuentes de datos (Salarios, GitHub, RemoteOK) en un único 
dataset maestro a nivel de tecnología/rol, optimizado para Looker Studio y Excel en español.
"""

# ============================================
# CONFIGURACIÓN DE PATHS
# ============================================
import sys
from pathlib import Path

scripts_path = Path(__file__).parent.parent
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

# ============================================
# IMPORTS
# ============================================
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
from utils.config import Config
from utils.logger import setup_logger


class DataIntegrator:
    """Clase para limpiar, transformar e integrar las fuentes de datos."""

    def __init__(self):
        self.logger = setup_logger()
        self.config = Config()
        self.config.create_directories()

        # Rutas de entrada
        self.salaries_path = self.config.DATA_RAW_PATH / "ds_salaries_2023.csv"
        self.github_path = self.config.DATA_RAW_PATH / "github_top_repos.json"
        self.jobs_path = self.config.DATA_RAW_PATH / "remoteok_jobs.json"

        # Rutas de salida
        self.master_csv_path = self.config.DATA_PROCESSED_PATH / "master_dataset.csv"
        self.charts_path = self.config.CHARTS_PATH
        self.csv_analysis_path = self.config.CSV_ANALYSIS_PATH

    def load_data(self):
        """Carga las 3 fuentes de datos."""
        self.logger.info("Cargando fuentes de datos...")
        self.df_salaries = pd.read_csv(self.salaries_path)
        self.logger.info(f"✓ Salarios cargados: {self.df_salaries.shape[0]} filas")

        with open(self.github_path, 'r', encoding='utf-8') as f:
            github_data = json.load(f)
        self.df_github = pd.DataFrame(github_data)
        self.logger.info(f"✓ GitHub cargado: {self.df_github.shape[0]} filas")
        self.logger.info(f"  Lenguajes únicos en GitHub: {list(self.df_github['language'].unique())}")

        with open(self.jobs_path, 'r', encoding='utf-8') as f:
            jobs_data = json.load(f)
        self.df_jobs = pd.DataFrame(jobs_data)
        self.logger.info(f"✓ Jobs cargados: {self.df_jobs.shape[0]} filas")

    def transform_salaries(self) -> pd.DataFrame:
        """Limpia y agrega datos de salarios por categoría tecnológica."""
        self.logger.info("Transformando datos de salarios...")
        df = self.df_salaries.copy()

        exp_map = {'EN': 'Entry', 'MI': 'Mid', 'SE': 'Senior', 'EX': 'Executive'}
        df['experience_level'] = df['experience_level'].map(exp_map).fillna('Unknown')

        def categorize_role(title):
            title = str(title).lower()
            if any(x in title for x in ['data scientist', 'machine learning', 'ml', 'ai']):
                return 'Data Science / AI'
            elif any(x in title for x in ['data engineer', 'data analytics', 'analyst']):
                return 'Data Engineering / Analytics'
            elif any(x in title for x in ['software engineer', 'developer', 'programmer']):
                return 'Software Engineering'
            elif any(x in title for x in ['devops', 'cloud', 'sysadmin']):
                return 'DevOps / Cloud'
            elif any(x in title for x in ['manager', 'director', 'chief']):
                return 'Management'
            else:
                return 'Other Tech'

        df['tech_category'] = df['job_title'].apply(categorize_role)

        salary_agg = df.groupby('tech_category').agg(
            avg_salary_usd=('salary_in_usd', 'mean'),
            median_salary_usd=('salary_in_usd', 'median'),
            total_records=('salary_in_usd', 'count'),
            remote_ratio_avg=('remote_ratio', 'mean')
        ).reset_index()

        salary_agg['remote_percentage'] = salary_agg['remote_ratio_avg'].round(1)
        salary_agg = salary_agg.drop(columns=['remote_ratio_avg'])

        self.logger.info(f"✓ Agregación de salarios completada: {salary_agg.shape[0]} categorías")
        self.logger.info(f"  Categorías de salarios: {list(salary_agg['tech_category'])}")
        return salary_agg

    def transform_github(self) -> pd.DataFrame:
        """Agrega datos de GitHub y los mapea a categorías amplias para fusionar."""
        self.logger.info("Transformando datos de GitHub...")
        df = self.df_github.copy()

        # Mapeo explícito de lenguajes a categorías
        lang_to_category = {
            'Python': 'Data Science / AI',
            'JavaScript': 'Software Engineering',
            'TypeScript': 'Software Engineering',
            'Rust': 'Software Engineering',
            'Go': 'DevOps / Cloud'
        }

        # Aplicar el mapeo
        df['tech_category'] = df['language'].map(lang_to_category)

        # Verificar que el mapeo funcionó
        mapped_count = df['tech_category'].notna().sum()
        self.logger.info(f"✓ Lenguajes mapeados correctamente: {mapped_count} de {len(df)}")

        if mapped_count == 0:
            self.logger.error("✗ ERROR: Ningún lenguaje fue mapeado. Revisar datos de GitHub.")
            self.logger.info(f"Lenguajes encontrados: {df['language'].unique()}")

        # Agrupar por categoría
        github_agg = df.groupby('tech_category').agg(
            total_repos=('repo_name', 'count'),
            avg_stars=('stars', 'mean'),
            total_stars=('stars', 'sum'),
            avg_forks=('forks', 'mean')
        ).reset_index()

        # Eliminar filas con categoría NaN (si las hay)
        github_agg = github_agg.dropna(subset=['tech_category'])

        self.logger.info(f"✓ Agregación de GitHub completada: {github_agg.shape[0]} categorías")
        self.logger.info(f"  Categorías de GitHub: {list(github_agg['tech_category'])}")
        return github_agg

    def transform_jobs(self) -> pd.DataFrame:
        """Agrega ofertas de empleo por tecnología detectada en tags."""
        self.logger.info("Transformando datos de ofertas de empleo...")
        df = self.df_jobs.copy()

        def extract_main_tech(tags_str):
            if pd.isna(tags_str):
                return 'Other'
            tags = str(tags_str).lower().split(', ')
            if any(t in tags for t in ['python', 'django', 'flask', 'fastapi', 'data', 'machine-learning', 'ai']):
                return 'Data Science / AI'
            elif any(t in tags for t in ['javascript', 'react', 'vue', 'angular', 'node', 'typescript', 'rust', 'go', 'java', 'backend']):
                return 'Software Engineering'
            elif any(t in tags for t in ['devops', 'docker', 'kubernetes', 'aws', 'azure', 'gcp']):
                return 'DevOps / Cloud'
            else:
                return 'Other Tech'

        df['tech_category'] = df['tags'].apply(extract_main_tech)

        jobs_agg = df.groupby('tech_category').agg(
            active_job_openings=('id', 'count'),
            avg_job_salary=('salary_avg', 'mean')
        ).reset_index()

        self.logger.info(f"✓ Agregación de empleos completada: {jobs_agg.shape[0]} categorías")
        self.logger.info(f"  Categorías de empleos: {list(jobs_agg['tech_category'])}")
        return jobs_agg

    def integrate_all(self) -> pd.DataFrame:
        """Fusiona las 3 fuentes en un único dataset maestro."""
        self.logger.info("=" * 60)
        self.logger.info("INICIANDO INTEGRACIÓN DE FUENTES DE DATOS")
        self.logger.info("=" * 60)

        df_sal = self.transform_salaries()
        df_gh = self.transform_github()
        df_jobs = self.transform_jobs()

        # Fusionar usando outer join para conservar todas las categorías de todas las fuentes
        master_df = df_sal.merge(df_gh, on='tech_category', how='outer')
        master_df = master_df.merge(df_jobs, on='tech_category', how='outer')

        # Rellenar nulos
        master_df['total_repos'] = master_df['total_repos'].fillna(0).astype(int)
        master_df['avg_stars'] = master_df['avg_stars'].fillna(0).round(0)
        master_df['total_stars'] = master_df['total_stars'].fillna(0).astype(int)
        master_df['avg_forks'] = master_df['avg_forks'].fillna(0).round(0)
        master_df['active_job_openings'] = master_df['active_job_openings'].fillna(0).astype(int)
        master_df['avg_job_salary'] = master_df['avg_job_salary'].fillna(master_df['avg_salary_usd'])

        # Calcular KPIs derivados (Índice de Demanda del Mercado)
        max_stars = master_df['avg_stars'].max() if master_df['avg_stars'].max() > 0 else 1
        max_jobs = master_df['active_job_openings'].max() if master_df['active_job_openings'].max() > 0 else 1

        master_df['stars_score'] = ((master_df['avg_stars'] / max_stars) * 100).round(1)
        master_df['jobs_score'] = ((master_df['active_job_openings'] / max_jobs) * 100).round(1)
        master_df['market_demand_index'] = ((master_df['stars_score'] + master_df['jobs_score']) / 2).round(1)

        # Ordenar por índice de demanda
        master_df = master_df.sort_values('market_demand_index', ascending=False).reset_index(drop=True)

        self.logger.info(f"✓ Dataset maestro creado: {master_df.shape[0]} filas, {master_df.shape[1]} columnas")
        self.logger.info(f"  Categorías finales: {list(master_df['tech_category'])}")
        return master_df

    def save_outputs(self, master_df: pd.DataFrame):
        """Guarda el CSV maestro y genera gráficos EDA."""
        self.logger.info("Guardando salidas y generando visualizaciones...")

        # Guardar CSV con formato compatible con Excel en español
        master_df.to_csv(self.master_csv_path, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        self.logger.info(f"✓ CSV Maestro guardado en: {self.master_csv_path}")

        # Gráfico 1: Salario vs Demanda de Mercado
        plt.figure(figsize=(10, 6))
        sns.scatterplot(
            data=master_df,
            x='market_demand_index',
            y='avg_salary_usd',
            size='total_records',
            sizes=(100, 500),
            hue='tech_category',
            palette='viridis',
            alpha=0.8
        )
        plt.title('Salario Promedio vs Índice de Demanda del Mercado Tech', fontsize=14, fontweight='bold')
        plt.xlabel('Índice de Demanda del Mercado (0-100)', fontsize=12)
        plt.ylabel('Salario Promedio (USD)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)

        for i, row in master_df.iterrows():
            plt.annotate(row['tech_category'], (row['market_demand_index'], row['avg_salary_usd']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)

        chart1_path = self.charts_path / "salario_vs_demanda.png"
        plt.tight_layout()
        plt.savefig(chart1_path, dpi=300)
        plt.close()
        self.logger.info(f"✓ Gráfico 1 guardado: {chart1_path}")

        # Gráfico 2: Ofertas de Empleo Activas por Categoría
        plt.figure(figsize=(10, 6))
        sns.barplot(
            data=master_df.sort_values('active_job_openings', ascending=True),
            x='active_job_openings',
            y='tech_category',
            palette='mako',
            hue='tech_category',
            legend=False
        )
        plt.title('Ofertas de Empleo Tech Activas por Categoría', fontsize=14, fontweight='bold')
        plt.xlabel('Número de Ofertas', fontsize=12)
        plt.ylabel('Categoría Tecnológica', fontsize=12)

        chart2_path = self.charts_path / "ofertas_empleo_por_tecnologia.png"
        plt.tight_layout()
        plt.savefig(chart2_path, dpi=300)
        plt.close()
        self.logger.info(f"✓ Gráfico 2 guardado: {chart2_path}")

        # Guardar CSV de KPIs
        kpi_df = master_df[['tech_category', 'avg_salary_usd', 'active_job_openings', 'remote_percentage', 'market_demand_index']]
        kpi_csv_path = self.csv_analysis_path / "kpi_resumen_tecnologico.csv"
        kpi_df.to_csv(kpi_csv_path, index=False, sep=';', decimal=',', encoding='utf-8-sig')
        self.logger.info(f"✓ CSV de KPIs guardado: {kpi_csv_path}")


def main():
    """Función principal del pipeline de integración."""
    integrator = DataIntegrator()

    try:
        integrator.load_data()
        master_df = integrator.integrate_all()
        integrator.save_outputs(master_df)

        print("\n" + "=" * 60)
        print("✓ INTEGRACIÓN Y TRANSFORMACIÓN COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        print("Archivos generados:")
        print(f"  1. Dataset Maestro: {integrator.master_csv_path}")
        print(f"  2. Gráfico EDA 1: {integrator.charts_path / 'salario_vs_demanda.png'}")
        print(f"  3. Gráfico EDA 2: {integrator.charts_path / 'ofertas_empleo_por_tecnologia.png'}")
        print(f"  4. KPIs CSV: {integrator.csv_analysis_path / 'kpi_resumen_tecnologico.csv'}")
        print("=" * 60)

        # Mostrar resumen del dataset maestro
        print("\nResumen del Dataset Maestro:")
        print(master_df[['tech_category', 'avg_salary_usd', 'total_repos', 'avg_stars', 'active_job_openings', 'market_demand_index']].to_string(index=False))

    except Exception as e:
        print(f"\n ERROR DURANTE LA INTEGRACIÓN: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()