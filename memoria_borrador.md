**Análisis exploratorio de datos de juegos de mesa — Tabletop-games-EDA**

Fecha: 2026-05-19


Índice
------
- Introducción y objetivos
- Fuentes de datos
- Preprocesado y limpieza
- Metodología de análisis
- Resultados principales
- Visualizaciones y tablas (referencia)
- Reproducibilidad y ejecución
- Limitaciones
- Conclusiones y próximos pasos
- Anexos y referencias

Introducción y objetivos
------------------------

Contexto
~~~~~~~~

BoardGameGeek (BGG) es una fuente extensa de metadatos sobre juegos de mesa: características de los juegos, valoraciones, número de propietarios (`owned`), listas de deseos (`wishing`/`wanting`), autores, artistas, mecánicas, categorías y rankings. El proyecto Tabletop-games-EDA organiza estos datos y aplica técnicas de EDA para extraer patrones relevantes.

Desde el punto de vista del ecosistema digital, BGG se ha consolidado como una referencia central para la comunidad de juegos de mesa. Según fuentes públicas, la plataforma fue lanzada en enero de 2000 por Scott Alden y Derk Solko, y combina base de datos, foros y sistema de valoración colaborativa. En la actualidad, su catálogo incluye más de 150.000 títulos y concentra una comunidad activa de gran tamaño, lo que la convierte en una infraestructura de datos especialmente útil para estudios descriptivos y comparativos de diseño lúdico.

El valor analítico de BGG no está solo en el volumen de datos, sino en la estructura relacional de su información: juegos, diseñadores, artistas, editoriales, mecánicas y categorías se encuentran enlazados y permiten análisis multicapas. Además, su sistema de puntuación y ranking facilita comparar recepción crítica y popularidad relativa entre títulos, lo que justifica su uso como fuente principal en esta memoria técnica.

Objetivos
~~~~~~~~~

1. Describir la colección de juegos: distribuciones de jugadores, edad mínima, duración de partida y complejidad (`weight`).
2. Identificar categorías, mecánicas, diseñadores y artistas más frecuentes en la muestra.
3. Contrastar las listas de `top` juegos según `rank_boardgame` y según una métrica de interés (suma de `owned + wishing + wanting`).
4. Generar visualizaciones reproducibles y un conjunto de tablas de apoyo para investigación o diseño de juegos.

Hipótesis de trabajo
~~~~~~~~~~~~~~~~~~~~

Antes de iniciar el análisis se plantearon las siguientes hipótesis:

1. La mayor parte de los juegos del dataset estará pensada para grupos pequeños, especialmente entre 2 y 4 jugadores, con duraciones medias cortas o moderadas.
2. Los juegos mejor valorados tenderán a presentar una complejidad mayor (`weight`) y una duración más larga que el promedio.
3. La popularidad medida por `interest = owned + wishing + wanting` no coincidirá exactamente con el ranking oficial, por lo que ranking e interés aportarán lecturas complementarias.
4. Las variables de complejidad, duración y valoración formarán un patrón multivariante reconocible, aunque no perfectamente lineal.

Fuentes de datos
----------------

Archivos principales en el repositorio:

- [data/source/bgg_games.csv](data/source/bgg_games.csv)
- [data/boardgame-geek-dataset_organized.csv](data/boardgame-geek-dataset_organized.csv)
- [data/source/game_categories.csv](data/source/game_categories.csv)
- [data/source/game_mechanics.csv](data/source/game_mechanics.csv)
- [data/source/game_designers.csv](data/source/game_designers.csv)
- [data/source/game_artists.csv](data/source/game_artists.csv)

Notebooks principales:

- [analysis.ipynb](analysis.ipynb) — análisis exploratorio y visualizaciones principales.
- [limpieza.ipynb](limpieza.ipynb) — pasos de limpieza y transformación.
- [graficos.ipynb](graficos.ipynb) — visualizaciones suplementarias.

Columnas relevantes (ejemplos)

- `row_id`: identificador del juego.
- `min_players`, `max_players`: rango de jugadores.
- `playingtime`: duración media de la partida.
- `minimum_age`: edad mínima recomendada.
- `weight`: complejidad (BoardGameGeek weight).
- `owned`, `wishing`, `wanting`: indicadores de interés/propiedad.
- `rank_boardgame`: posición en ranking (puede contener 'Not Ranked').

Preprocesado y limpieza
-----------------------

Operaciones aplicadas (resumen técnico):

1. Lectura y revisión de cardinalidad y nulos para decidir columnas a usar.
2. Conversión de tipos: por ejemplo, `rank_boardgame` se convierte a numérico con coerción de errores (`pd.to_numeric(..., errors='coerce')`).
3. Eliminación/filtrado de valores no informativos: p. ej. filas con artistas o diseñadores `'(Uncredited)'` se excluyen de ciertos análisis.
4. Tratamiento de nulos: imputación mínima o exclusión según el contexto de la variable y la visualización.
5. Creación de variables derivadas: `interest = owned + wishing + wanting` para medir popularidad/atracción.
6. Uniones por `row_id` entre tablas auxiliares (diseñadores, mecánicas, categorías, artistas) para agregar y cruzar información.

Notas de implementación
~~~~~~~~~~~~~~~~~~~~~~~

- En los notebooks se usan `pandas`, `numpy`, `matplotlib` y `seaborn` para análisis y gráficos.
- El archivo `bgg_id_batch_downloader.py` puede usarse para actualizar/descargar datos si se requiere reconstruir la base.

Metodología de análisis
-----------------------

Enfoque general
~~~~~~~~~~~~~~~

- Estadística descriptiva: se calcularon media, mediana, desviación estándar, mínimos, máximos y asimetría (`skew`) para las variables numéricas más relevantes.
- Análisis de distribución: se utilizaron histogramas con KDE para observar concentración, colas y sesgo en `min_players`, `max_players`, `playingtime`, `minimum_age` y `weight`.
- Detección de outliers: se recurrió a boxplots para identificar valores atípicos y rangos poco frecuentes.
- Análisis categórico: se revisaron frecuencias absolutas de categorías, mecánicas, diseñadores y artistas para conocer qué elementos dominan el conjunto de datos.
- Análisis comparativo: se construyeron dos subconjuntos, `top100` por `rank_boardgame` y `top100` por `interest`, para contrastar popularidad editorial frente a interés del público.
- Agregaciones por entidad: se calcularon tablas resumen como `total_mecanica` y `autor_por_mecanica` para identificar combinaciones relevantes entre mecánicas y autores.

Desglose del análisis
~~~~~~~~~~~~~~~~~~~~~

1. Carga de datos y preparación inicial: lectura de `bgg_games.csv` y de las tablas auxiliares de categorías, mecánicas, diseñadores y artistas.
2. Normalización de campos: conversión de `rank_boardgame` a tipo numérico y exclusión de valores no interpretables en análisis concretos.
3. Construcción de variables derivadas: generación de `interest = owned + wishing + wanting` como aproximación de atracción o demanda.
4. Análisis univariado: revisión de estadísticas descriptivas y gráficos de distribución para cada variable principal.
5. Análisis bivariado: exploración de relaciones entre `average_rating`, `weight`, `playingtime`, `rank_boardgame` y otras variables numéricas.
6. Análisis por segmentos: comparación de la composición de los `top100` por ranking y por interés.
7. Síntesis visual: consolidación de figuras globales para incluir en la memoria técnica.

Procedimiento reproducible (pasos concretos)

1. Ejecutar la limpieza en [limpieza.ipynb](limpieza.ipynb) para obtener CSVs intermedios si se generan.
2. Abrir [analysis.ipynb](analysis.ipynb) y ejecutar celdas en orden: carga de datos → estadísticas descriptivas → visualizaciones.
3. Generar subconjuntos: limpieza de `rank_boardgame` y cálculo de `interest`.
4. Crear visualizaciones y exportar tablas de resultados (`autor_por_mecanica`, `total_mecanica`, tablas top N).

Figuras y resultados añadidos
-----------------------------

Las figuras principales se han generado en la carpeta [figures](figures) y el informe final se ha exportado como [memoria_tecnica_tabletop_games_eda.pdf](memoria_tecnica_tabletop_games_eda.pdf).

Figura 1. Distribuciones numéricas

Esta figura resume la forma de las variables numéricas principales mediante histogramas con KDE. Permite ver rápidamente el sesgo de `playingtime`, la concentración de `min_players` y `max_players` y la distribución moderada de `weight`.

![Distribuciones numéricas](figures/fig_01_distribuciones_numericas.png)

Figura 2. Frecuencias globales

Esta figura sintetiza qué categorías, mecánicas, diseñadores y artistas dominan el dataset completo. Es útil para entender la composición general de la colección.

![Frecuencias globales](figures/fig_02_top_globales.png)

Figura 3. Top100 por ranking

Esta figura compara las entidades más frecuentes dentro de los juegos mejor posicionados por ranking. Destaca la presencia de mecánicas complejas y juegos orientados a la optimización o al juego en solitario.

![Top100 por ranking](figures/fig_03_top100_ranking.png)

Figura 4. Top100 por interés

Esta figura muestra qué elementos aparecen con más fuerza cuando se ordena por interés público. La comparación con la figura anterior evidencia diferencias entre prestigio crítico e interés de la comunidad.

![Top100 por interés](figures/fig_04_top100_interes.png)

Resultados principales
---------------------

Se han extraído estadísticas agregadas y listas `top` directamente de los archivos de datos. A continuación se muestran los resultados principales encontrados (valores numéricos calculados sobre `data/source/bgg_games.csv` y archivos auxiliares en `data/source/`):

Estadísticas numéricas resumen

- `min_players`: n=28462, media=1.94, mediana=2.00, std=0.69, min=0.0, max=9.0, skew=1.32
- `max_players`: n=28462, media=4.70, mediana=4.00, std=2.55, min=0.0, max=30.0, skew=2.71
- `playingtime` (minutos): n=28462, media=75.27, mediana=45.0, std=102.59, min=1.0, max=1200.0, skew=5.33
- `minimum_age`: n=28462, media=9.84, mediana=10.0, std=3.51, min=0.0, max=21.0, skew=-0.77
- `weight`: n=28462, media=1.98, mediana=1.9269, std=0.78, min=1.0, max=4.817, skew=0.69

Interpretación rápida:

- Las medianas de `min_players` y `max_players` (2 y 4) muestran que gran parte de los juegos están pensados para grupos pequeños (2–4 jugadores).
- `playingtime` presenta una distribución muy sesgada a la derecha (skew alto), con muchos títulos cortos y una cola de juegos con duración larga (hasta 1200 minutos en el dataset).
- `weight` (complejidad) se mantiene en torno a 2 en la media/mediana, indicando una muestra con tendencia a juegos de complejidad baja-moderada.

Análisis univariante y hallazgos

- `min_players` y `max_players` confirman que el diseño dominante se orienta a partidas de 2 a 4 personas.
- `playingtime` concentra el grueso de los juegos en valores bajos o medios, aunque existe una cola larga de títulos de duración muy alta.
- `minimum_age` se sitúa alrededor de 10 años, lo que sugiere un catálogo orientado a público familiar o juvenil-adulto.
- `weight` presenta una distribución moderada: la mayoría de juegos no son extremadamente complejos, aunque existen títulos más pesados que elevan el máximo observado.
- En conjunto, la muestra describe una colección donde predominan juegos accesibles, con tiempo de partida razonable y complejidad contenida.

Top categorías y mecánicas (global)

Top 10 categorías (conteos):

1. Card Game — 11562
2. Expansion for Base-game — 7194
3. Fantasy — 5900
4. Wargame — 5242
5. Fighting — 3530
6. Science Fiction — 3315
7. Dice — 3163
8. Party Game — 2838
9. Adventure — 2761
10. Economic — 2592

Top 10 mecánicas (conteos):

1. Dice Rolling — 10172
2. Hand Management — 8638
3. Variable Player Powers — 6214
4. Set Collection — 5064
5. Cooperative Game — 4181
6. Open Drafting — 4021
7. Hexagon Grid — 3324
8. Tile Placement — 3315
9. Modular Board — 3305
10. Solo / Solitaire Game — 3068

Top diseñadores y artistas (global)

Top 10 diseñadores (conteos):

1. (Uncredited) — 1487
2. Reiner Knizia — 472
3. Eric M. Lang — 313
4. Nate French — 214
5. Steve Jackson (I) — 182
6. Wolfgang Kramer — 173
7. Uwe Rosenberg — 167
8. Bruno Cathala — 166
9. Scott Almes — 155
10. Richard Garfield — 149

Top 10 artistas (conteos):

1. Rodger B. MacGowan — 442
2. (Uncredited) — 435
3. Franz Vohwinkel — 426
4. Michael Menzel — 291
5. Klemens Franz — 286
6. Redmond Aksel Simonsen — 265
7. Mark Simonitch — 248
8. John Kovalic — 217
9. Dennis Lohausen — 216
10. Mihajlo Dimitrievski — 215

Top 100: comparativa `rank_boardgame` vs `interest`

- Ambos subconjuntos (`top100` por `rank_boardgame` y por `interest`) están completos (100 registros cada uno en el dataset actual).
- Agregaciones sobre los `top100` muestran diferencias en entidades dominantes:

Top entidades en `top100` por `rank_boardgame` (ejemplos):

- Diseñadores más frecuentes (en top100 por ranking): Rob Daviau (5), Matt Leacock (5), Paul Dennen (5), Uwe Rosenberg (5), Alexander Pfister (4), ...
- Mecánicas más frecuentes (en top100 por ranking): Solo / Solitaire Game (54), Hand Management (53), Variable Player Powers (47), Variable Set-up (42), End Game Bonuses (37), ...
- Categorías más frecuentes (en top100 por ranking): Economic (35), Fantasy (29), Science Fiction (20), Exploration (19), Adventure (18), ...

Top entidades en `top100` por `interest` (ejemplos):

- Diseñadores más frecuentes (en top100 por interest): Uwe Rosenberg (5), Matt Leacock (4), Antoine Bauza (4), Bruno Cathala (3), Vlaada Chvátil (3), ...
- Mecánicas más frecuentes (en top100 por interest): Hand Management (55), Variable Player Powers (36), Variable Set-up (32), Set Collection (31), End Game Bonuses (29), ...
- Categorías más frecuentes (en top100 por interest): Card Game (36), Fantasy (23), Economic (21), Adventure (16), Animals (14), ...

Interpretación:

- La composición de mecánicas y categorías en `top100` por ranking tiende a incluir títulos con solitario/solitaire y mecanismos que favorecen diseño complejo, mientras que el `top100` por interés muestra mayor presencia de `Hand Management` y `Card Game`, y un giro hacia títulos con mayor alcance o popularidad social.
- Algunos diseñadores aparecen en ambos listados (por ejemplo Uwe Rosenberg y Matt Leacock), pero su prominencia relativa cambia según la métrica usada (valoración crítica vs atención/propiedad pública).

Análisis bivariante y hallazgos

La matriz de correlaciones muestra relaciones claras entre varias variables:

- `weight` y `playingtime` presentan una correlación positiva moderada-alta (0.533), lo que sugiere que los juegos más complejos suelen durar más.
- `average_rating` y `weight` también muestran una relación positiva relevante (0.519), indicando que los títulos mejor valorados tienden a ser algo más complejos.
- `rank_boardgame` se relaciona de forma negativa con `average_rating` (-0.720) y con `weight` (-0.405), lo que es coherente con la lógica del ranking: cuanto mejor es la posición, mayor valoración y complejidad relativa suelen aparecer.
- `average_rating` y `playingtime` mantienen una asociación positiva (0.270), aunque menos intensa que la observada con `weight`.
- `min_players` y `max_players` se relacionan entre sí (0.358), pero muestran una asociación débil o negativa con la valoración, lo que sugiere que el tamaño de grupo no explica por sí solo el éxito crítico.

En términos interpretativos, el análisis bivariante refuerza la idea de que complejidad y duración forman un eje común, mientras que el ranking parece capturar, al menos parcialmente, ese patrón junto con la valoración media.

Análisis multivariante y hallazgos

El análisis multivariante se ha apoyado en el `pairplot` de [graficos.ipynb](graficos.ipynb) y en la matriz de correlaciones entre `rank_boardgame`, `average_rating`, `release_year`, `playingtime`, `weight`, `min_players`, `max_players`, `bayes_average` e `interest`.

- Las visualizaciones combinadas muestran que los juegos con mejor valoración tienden a agruparse en rangos de `weight` más altos y `playingtime` algo mayor, aunque sin una frontera estricta.
- Las categorías de `average_rating` usadas en el `pairplot` permiten observar cómo los juegos mejor valorados se concentran en bandas diferenciadas de complejidad y duración.
- `bayes_average` mantiene una asociación fuerte con `interest` (0.676), lo que indica que ambas métricas reflejan, desde ángulos distintos, una noción parecida de atracción o recepción del juego.
- `release_year` muestra correlaciones débiles con el resto de variables, por lo que en esta muestra no actúa como factor dominante para explicar valoración, complejidad o popularidad.
- En conjunto, la lectura multivariante sugiere un perfil de juegos donde la valoración, la duración y la complejidad se mueven de forma conjunta, mientras que el año de publicación explica menos variación de la esperada.


Visualizaciones y tablas (referencia)
------------------------------------

Gráficos incluidos en los notebooks (ejemplos):

- Histogramas con KDE para variables numéricas (en [analysis.ipynb](analysis.ipynb)).
- Boxplots para detectar outliers (en [analysis.ipynb](analysis.ipynb)).
- Barras Top 15 de artistas/diseñadores/categorías/mecánicas con anotaciones de conteo y porcentaje (en [analysis.ipynb](analysis.ipynb)).
- Tablas agregadas: `total_mecanica`, `autor_por_mecanica` — generadas en celdas de [analysis.ipynb](analysis.ipynb).

Reproducibilidad y ejecución
---------------------------

Requisitos de entorno (sugerido)

- Python 3.9+ o 3.10
- Paquetes: `pandas`, `numpy`, `matplotlib`, `seaborn`, `jupyter`.

Comandos rápidos para preparar entorno (ejemplo con `pip`):

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt  # o pip install pandas numpy matplotlib seaborn jupyter
```

Orden recomendado de ejecución

1. `limpieza.ipynb` — ejecutar para aplicar transformaciones y generar datos preparados.
2. `analysis.ipynb` — ejecutar para reproducir estadísticas y figuras.
3. `graficos.ipynb` — ejecutar si se desean figuras adicionales o exportaciones.

Limitaciones
------------

- Calidad de los datos: datos faltantes o con formato inconsistente (p. ej. `Not Ranked`) afectan análisis.
- Sesgo de cobertura: `owned`, `wishing` y `wanting` son señales de interés pero no una muestra aleatoria de la comunidad.
- Decisiones de filtrado: excluir elementos `(Uncredited)` o coercionar `rank_boardgame` puede cambiar resultados de top lists.
- Temporalidad: los datos reflejan el estado de la descarga y pueden variar con actualizaciones de BGG.

Conclusiones y próximos pasos
----------------------------

Conclusiones

Este proyecto ha permitido caracterizar una colección amplia de juegos de mesa a partir de información estructurada procedente de BoardGameGeek. El análisis descriptivo confirma que la mayor parte de la muestra se concentra en juegos pensados para grupos reducidos, con duraciones relativamente cortas o medias y complejidades moderadas. A partir de esta base, las visualizaciones generadas han servido para identificar las distribuciones principales, los valores atípicos y la presencia de asimetrías relevantes en las variables numéricas.

En el plano temático, las categorías y mecánicas más frecuentes muestran un perfil claramente reconocible: abundancia de juegos de cartas, sistemas de gestión de mano, lanzamiento de dados, construcción de conjunto y poderes variables. Esta concentración ayuda a entender qué diseños están más representados en el catálogo analizado y, por tanto, qué patrones aparecen con más fuerza cuando se estudia la oferta global de juegos.

La comparación entre el ranking oficial y la métrica de interés construida con `owned`, `wishing` y `wanting` aporta una lectura complementaria. Mientras que el ranking tiende a favorecer títulos con presencia fuerte de mecánicas complejas o de juego en solitario, el indicador de interés refleja una atención más amplia hacia juegos con una huella social y de popularidad más marcada. Esta diferencia es especialmente útil porque separa dos dimensiones que no siempre coinciden: prestigio crítico y tracción entre usuarios.

Desde el punto de vista del diseño de juegos, los resultados sugieren que existe una base sólida para orientar decisiones sobre número de jugadores, duración, mecánicas predominantes y nivel de complejidad. En otras palabras, el EDA no solo describe el dataset, sino que también ofrece un punto de partida razonable para decisiones de producto, segmentación de mercado o análisis comparativo de familias de juegos.

Verificación de hipótesis

- Hipótesis 1: confirmada. Los datos muestran una clara concentración en juegos de 2 a 4 jugadores y con tiempos de partida típicamente bajos o moderados.
- Hipótesis 2: parcialmente confirmada. La relación entre valoración, complejidad y duración es positiva, pero no absoluta; hay juegos bien valorados en distintos niveles de complejidad.
- Hipótesis 3: confirmada. El ranking y la métrica de interés no coinciden exactamente y capturan dimensiones diferentes de la popularidad.
- Hipótesis 4: confirmada de forma general. La matriz de correlaciones y el `pairplot` muestran un patrón multivariante consistente, aunque con relaciones no lineales y variables con peso desigual.

Limitaciones

Conviene interpretar los resultados con cautela. El dataset depende de la calidad y actualidad de la información pública de BoardGameGeek, por lo que puede contener nulos, valores heterogéneos o registros poco homogéneos entre tablas. Además, métricas como `owned`, `wishing` y `wanting` son proxies útiles de interés, pero no equivalen a una medición causal o representativa de la demanda real.

Próximos pasos

1. Incorporar un análisis de correlación entre variables como `weight`, `playingtime`, `rank_boardgame` y `average_rating`.
2. Profundizar en la evolución temporal por año de publicación para detectar tendencias de diseño.
3. Explorar un modelo predictivo sencillo para estimar interés o ranking a partir de atributos de juego.
4. Consolidar el informe final con exportación de tablas y figuras ya integradas.

En conjunto, el trabajo deja una base sólida para una memoria técnica completa, con resultados interpretables, visualizaciones consistentes y una narrativa analítica útil para continuar el estudio.

Anexos
------

- Lista de archivos de datos ya citados en la sección "Fuentes de datos".
- Fragmentos de código relevantes (ejemplos extraídos de `analysis.ipynb`):

```python
# Conversión de ranking y cálculo de top100
import pandas as pd
bgg_games = pd.read_csv('data/source/bgg_games.csv')
bgg_games['rank_boardgame'] = pd.to_numeric(bgg_games['rank_boardgame'], errors='coerce')
top100_bgg_games = bgg_games[bgg_games['rank_boardgame'].notna()].sort_values('rank_boardgame').head(100)

# Calculo de interest
bgg_games['interest'] = bgg_games['owned'].fillna(0) + bgg_games['wishing'].fillna(0) + bgg_games['wanting'].fillna(0)
interest_top100 = bgg_games.sort_values('interest', ascending=False).head(100)
```

Referencias
-----------

- BoardGameGeek: https://boardgamegeek.com
- Wikipedia - BoardGameGeek (historia y contexto): https://en.wikipedia.org/wiki/BoardGameGeek

---

Este documento queda preparado como versión final de la memoria técnica del proyecto.

