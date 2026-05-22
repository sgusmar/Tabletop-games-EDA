# EXPLORATORY DATA ANALYSIS SOBRE EL DATASET DE BOARDGAMEGEEK (BGG)

### Descripción breve

- Este repositorio contiene el análisis exploratorio (EDA) y la preparación de datos de un conjunto de juegos de mesa. Incluye notebooks con el flujo de trabajo, código reutilizable y los datos ya preparados para reproducir los resultados.

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

- Carpetas:
  - [src/](src/) — Código fuente y módulo Python.
  - [data/](data/) — Datos usados en el análisis (p. ej. [data/boardgames_ranks.csv](data/boardgames_ranks.csv)).
  - [notebooks/](notebooks/) — Notebooks de EDA y pasos intermedios (`EDA_draft.ipynb`, `graficos.ipynb`, `limpieza.ipynb`).
  - [utils/](utils/) — Funciones reutilizables (`utils/funciones.py`).
  - [img/](img/) — Imágenes y gráficos generados por los notebooks.

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

### Autores

- Proyecto en: GitHub — https://github.com/sgusmar/Tabletop-games-EDA
- Contribuidores:
  - Emilio Garrote Sánchez — GitHub: https://github.com/Emigarsan
  - Sandra Gusi Martinez - Github : https://github.com/sgusmar


