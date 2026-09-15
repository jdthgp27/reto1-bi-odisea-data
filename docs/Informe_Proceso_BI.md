1. **Título:** Informe de Creación de Tablero de Business Intelligence: Mercado Laboral Tech 2024 

2. **Autor:** Judit Giravent

3. **Fecha:** 15 de septiembre de 2026

  **1. Introducción y Selección de Herramientas** El objetivo de este proyecto es analizar el mercado laboral tecnológico actual, cruzando datos históricos de salarios con indicadores de demanda en tiempo real. Para la herramienta de BI, se ha seleccionado **Looker Studio** de Google, debido a su capacidad nativa para integrarse con Google Sheets, su gratuidad y su facilidad para compartir dashboards interactivos en la nube. Para el procesamiento de datos (ETL), se utilizó **Python** con librerías como Pandas y Requests.

  **2. Recolección y Preparación de Datos** Se implementó un pipeline ETL (Extracción, Transformación y Carga) para integrar tres fuentes de datos heterogéneas:

  - **Fuente 1 (CSV Histórico):** Dataset "Data Science Salaries 2023" (3,755 registros de salarios, roles y modalidad de trabajo).
  - **Fuente 2 (API Web - GitHub):** API REST de GitHub para extraer los 250 repositorios más populares en lenguajes clave (Python, JS, TS, Rust, Go) como indicador de popularidad tecnológica.
  - **Fuente 3 (API Web - Tiempo Real):** API pública de RemoteOK para obtener ofertas de empleo tech activas en el momento de la consulta.

  *[INSERTAR CAPTURA: Muestra el diagrama de flujo de tu proyecto o una captura de la carpeta `data/raw` con los 3 archivos]*

  **3. Importación y Conexión en Looker Studio** El dataset maestro (`master_dataset.csv`), ya limpio y unificado mediante Python, se importó a **Google Sheets**. Looker Studio se conectó directamente a esta hoja de cálculo mediante su conector nativo, lo que permite que el dashboard se actualice automáticamente cada vez que se refresquen los datos en la hoja de origen.

  *[INSERTAR CAPTURA: Pantalla de Looker Studio mostrando el panel de "Añadir datos" o la conexión con Google Sheets]*

  **4. Diseño de Visualizaciones y Decisiones de Diseño** El tablero se diseñó siguiendo una jerarquía visual clara para facilitar la toma de decisiones:

  - **Cabecera (KPIs):** Se utilizaron "Cuadros de resultados" para mostrar de un vistazo el Salario Promedio, el Índice de Demanda y el % de Trabajo Remoto.
  - **Cuerpo (Análisis Comparativo):** Un gráfico de dispersión para correlacionar Salario vs. Demanda, y un gráfico de barras para ver las ofertas activas por categoría.
  - **Interactividad:** Se añadió un filtro desplegable por "Categoría Tecnológica" para que el usuario pueda segmentar la información.
  - **Paleta de colores:** Se optó por tonos corporativos (azules y verdes) para transmitir profesionalidad y facilitar la lectura.

  *[INSERTAR CAPTURA: Una captura general de tu dashboard en Looker Studio]*

  **5. Análisis y Optimización** Se optimizó el rendimiento agregando los datos a nivel de categoría tecnológica antes de importarlos a Looker Studio. Esto reduce la carga de procesamiento en el navegador y hace que los filtros respondan de manera instantánea