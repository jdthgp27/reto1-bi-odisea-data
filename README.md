#  Dashboard BI: Análisis del Mercado Laboral Tech 2024

> **Reto 1 - Business Intelligence y Big Data | Odisea Data**  
> Pipeline ETL completo en Python + Dashboard interactivo en Looker Studio

##  Objetivo del Proyecto
Crear un tablero de Business Intelligence que integre múltiples fuentes de datos heterogéneas (CSV histórico y APIs web en tiempo real) para analizar salarios, demanda tecnológica y tendencias de trabajo remoto en el sector tech durante 2024.

![Dataset Maestro](outputs/screenchots/Dataset.png)

![Salario vs Demanda](outputs/screenchots/salariovsdemanda.png)

![Tendencias Trabajo Remoto](outputs/screenchots/tendenciasdetrabajoremoto%.png
)


## ️ Stack Tecnológico
- **Lenguaje:** Python 3.10+
- **ETL & Datos:** Pandas, NumPy, Requests, Loguru
- **Visualización EDA:** Matplotlib, Seaborn
- **BI Tool:** Looker Studio (Google)
- **Conector de Datos:** Google Sheets (actualización automática)

##  Estructura del Proyecto
```text
reto1-bi-odisea-data/
├── data/
│   ├── raw/              # Datos crudos extraídos (CSV + JSONs de APIs)
│   ├── processed/        # Dataset maestro unificado y limpio
│   ── external/         # Reportes de metadatos y diccionarios
├── scripts/
│   ├── extract/          # Extractores: Salarios, GitHub API, RemoteOK API
│   ├── transform/        # Limpieza, categorización e integración de fuentes
│   ── utils/            # Configuración, logging y cliente HTTP reutilizable
├── outputs/
│   ├── charts/           # Gráficos EDA generados automáticamente (PNG)
│   └── csv_analysis/     # KPIs derivados para análisis externo
├── reports/              # Informes técnicos y estructura de presentación
── dashboards/           # Enlaces públicos al dashboard de Looker Studio


Cómo Ejecutar el Pipeline ETL
1. Requisitos Previos
Python 3.10 o superior
Token de GitHub (Personal Access Token) configurado en .env
Conexión a internet activa (para llamadas a APIs)

2. Instalación

git clone https://github.com/jdthgp27/reto1-bi-odisea-data.git
cd reto1-bi-odisea-data
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

3. Configuración de Credenciales
Crea un archivo .env en la raíz del proyecto con tu token de GitHub:

GITHUB_TOKEN=ghp_tu_token_aqui


4. Ejecución por Fases
El pipeline está diseñado para ejecutarse manualmente fase por fase:

# Fase 1: Extracción de datos
python scripts/extract/extractor_salaries.py
python scripts/extract/extractor_github.py
python scripts/extract/extractor_remoteok.py

# Fase 2: Transformación e Integración
python scripts/transform/integracion.py


Nota: El script de integración genera automáticamente el master_dataset.csv, los gráficos EDA y los KPIs derivados.
Resultados Clave

Dataset Maestro Integrado
Se fusionaron 3 fuentes heterogéneas en un único dataset de 6 categorías tecnológicas y 14 métricas:

https://raw.githubusercontent.com/jdthgp27/reto1-bi-odisea-data/main/outputs/screenchots/Dataset.png

![Dataset Maestro](outputs/screenchots/Dataset.png)

Visualizaciones Principales

Gráfico de dispersión: Equilibrio entre salario promedio e índice de demanda del mercado.

https://raw.githubusercontent.com/jdthgp27/reto1-bi-odisea-data/main/outputs/screenchots/salariovsdemanda.png

![Salario vs Demanda](outputs/screenchots/salariovsdemanda.png)

Gráfico de barras: Distribución de ofertas de empleo tech activas en tiempo real.

https://raw.githubusercontent.com/jdthgp27/reto1-bi-odisea-data/main/outputs/screenchots/tendenciastrabajoremoto%.png

![Tendencias Trabajo Remoto](outputs/screenchots/tendenciastrabajoremoto%.png)

🔗 Dashboard Interactivo

Accede al tablero completo en Looker Studio con filtros dinámicos y actualización automática:
👉 Ver Dashboard en Looker Studio
📝 Entregables del Reto
✅ Archivo del tablero de BI (Link público de Looker Studio)
✅ Informe del proceso de creación (reports/informe_proceso.md)
✅ Visualizaciones y análisis clave (reports/analisis_kpi.md)
✅ Presentación para público no técnico (reports/presentacion_powerpoint.md)
✅ Código fuente documentado y reproducible

Hallazgos Destacados

Data Science / AI ofrece el mejor equilibrio entre alta demanda (61.1/100) y salarios competitivos ($143K).
DevOps / Cloud lidera indiscutiblemente el trabajo remoto con un 85.7%, consolidándose como el rol más flexible.
La popularidad en GitHub actúa como un indicador adelantado de demanda laboral antes de reflejarse en portales de empleo tradicionales.
Los roles de Management tienen los salarios más altos pero nula presencia en APIs públicas, sugiriendo un mercado cerrado basado en networking directo.

👤 Autor
Judit Giravent
Business Analytics Student | Odisea Data
LinkedIn | ✉️ linkedin.com/in/judit-giravent-27b167156

Proyecto desarrollado como parte del curso Business Intelligence y Big Data de Odisea Data. Septiembre 2026.