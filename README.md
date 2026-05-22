# EXPLORATORY DATA ANALYSIS SOBRE EL DATASET DE BOARDGAMEGEEK (BGG)
<div style="text-align: center;">
    <img src="src/img/logo.png" alt="BoardGameGeek">
</div>

### Descripción breve

- Este proyecto realiza un análisis exploratorio (EDA) de datos extraídos de BoardGameGeek con el fin de identificar patrones y relaciones relevantes entre características de los juegos (valoración, popularidad, complejidad, duración, número mínimo/máximo de jugadores, edad mínima, categorías y mecánicas).

- El enfoque incluye limpieza y normalización de tablas, cálculo de métricas resumen (p. ej. rating promedio y medida bayesiana), análisis univariante, bivariante y multivariante, así como la identificación de subconjuntos interesantes (top categorías, mecánicas y autores). Se generan visualizaciones y tablas resumen que respaldan las conclusiones y permiten comunicar hallazgos en informes y presentaciones.

- Los notebooks son reproducibles y están pensados para que un analista pueda replicar el flujo: cargar datos, aplicar transformaciones, ejecutar análisis estadísticos y generar gráficos listos para la presentación.

### Hipótesis planteadas

- H1: La mayoría de los juegos está diseñada para grupos pequeños (especialmente 2–4 jugadores); estas configuraciones y duraciones cortas/moderadas se asociarán a mejores valoraciones y mayor popularidad.
- H2: La complejidad (`weight`) y la duración están positivamente relacionadas con la valoración: los juegos mejor valorados tenderán a ser más complejos y algo más largos que la media.
- H3: La popularidad (sumatorio de las columnas `owned` y `wishing`) y la frecuencia de mecánicas/categorías no son uniformes; ciertas mecánicas, categorías, y autores/artistas alcanzarán valoraciones superiores en sus respectivos subconjuntos.
- H4: La edad mínima influye en la valoración y popularidad, ya que determina en parte la complejidad objetivo del juego.

### Tecnologías utilizadas

- Python 3
- Pandas, NumPy
- Matplotlib, Seaborn
- Jupyter / JupyterLab
- Otras utilidades en `requirements.txt`

### Estructura del repositorio

- Archivos principales:
  - [main.ipynb](main.ipynb) — Notebook principal de referencia.
  - [requirements.txt](requirements.txt) — Lista de dependencias.
  - [EDA_Tabletop_Games_presentation.pdf](EDA_Tabletop_Games_presentation.pdf) — Presentación del proyecto.
  - [Tabletop_games_memoria_tecnica.pdf](Tabletop_games_memoria_tecnica.pdf) — Memoria técnica del trabajo.

- Carpetas:
  - [src/](src/) — Código fuente y módulo Python.
  - [src/data/](src/data/) — Datos usados en el análisis. Contiene:
    - `boardgames_ranks.csv`
    - `tables/` con archivos de las tablas depuradas y filtradas. Por ejemplo, [bgg_games.csv](src/data/tables/bgg_games.csv)
  - [src/notebooks/](src/notebooks/) — Notebooks y scripts auxiliares: [analysis.ipynb](src/notebooks/analysis.ipynb), [EDA_draft.ipynb](src/notebooks/EDA_draft.ipynb), etc.
  - [src/utils/](src/utils/) — Funciones reutilizables (`src/utils/funciones.py`).
  - [src/img/](src/img/) — Imágenes y gráficos generados (varios PNG y logos), p. ej. `top15_global.png`, `monovariante_anyo.png`, `bivariante_rating_weight.png`, etc.

### Instrucciones de reproducción

1. Clonar el repositorio:

```
git clone https://github.com/sgusmar/Tabletop-games-EDA.git
cd Tabletop-games-EDA
```

2. Crear y activar un entorno virtual (Windows PowerShell):

```
python -m venv venv
venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
```

3. Abrir `main.ipynb` o cualquiera de los notebooks en `notebooks/` con JupyterLab/Jupyter Notebook y ejecutar las celdas en orden.

### Principales conclusiones

- Mercado en crecimiento: aumenta el número de juegos publicados y la complejidad desde los 2000, aunque los juegos ligeros siguen siendo predominantes.
- Valoraciones por edad y jugadores: juegos con edad mínima 14 muestran medias más altas; edad 11 presenta valoraciones más estables. Formatos de 2–4 jugadores concentran las medianas de rating más elevadas.
- Temática y mecánicas: categorías frecuentes (card game, economic, fantasy) y mecánicas como hand management y variable player powers están asociadas a mejores valoraciones en sus subconjuntos.
- Autores concentrados: ciertos diseñadores/artistas destacan con mejores valoraciones dentro de los segmentos más representativos del dataset.

---

### Autores

- Proyecto en: GitHub — https://github.com/sgusmar/Tabletop-games-EDA
- Contribuidores:
  - Emilio Garrote Sánchez — GitHub: https://github.com/Emigarsan
  - Sandra Gusi Martinez - Github : https://github.com/sgusmar


