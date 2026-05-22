import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def cargar_tabla_juegos(tabla=None):
    """
    Carga una tabla de juegos.
    - Si 'tabla' es un DataFrame, lo devuelve directamente.
    - Si 'tabla' es el nombre (str) de una variable global que es DataFrame, la devuelve.
    - En otro caso, interpreta 'tabla' como nombre de archivo (sin .csv) y carga src/data/tables/{tabla}.csv.
    - Si no se pasa nada, por defecto carga 'bgg_games.csv'.
    """
    # Si ya nos pasan un DataFrame, devolverlo tal cual
    if isinstance(tabla, pd.DataFrame):
        # Evitamos leer desde disco si ya tenemos el DataFrame en memoria
        print("Tabla cargada desde la variable.")
        return tabla

    # Si nos pasan el nombre de la variable y existe en el espacio global como DataFrame, devolverla
    if isinstance(tabla, str) and tabla in globals() and isinstance(globals()[tabla], pd.DataFrame):
        print(f"Tabla cargada desde la variable: {tabla}")
        return globals()[tabla]

    # Determinar el nombre del archivo a cargar (por defecto 'bgg_games')
    tabla_name = tabla if isinstance(tabla, str) else 'bgg_games'
    print(f"Cargando tabla desde archivo: src/data/tables/{tabla_name}.csv")
    # Leer el CSV correspondiente y devolver el DataFrame
    return pd.read_csv(f'src/data/tables/{tabla_name}.csv')

def clasificar_columna(s: pd.Series, threshold: int = 50) -> str:
    """Clasifica una columna de un DataFrame en tipos simples.

    Devuelve una de las siguientes etiquetas:
      - 'numerico_continuo': variable numérica con muchos valores únicos.
      - 'numerico_discreto': variable numérica con pocos valores distintos (enteros o floats con valores enteros).
      - 'categorico': variable no numérica.

    Parámetros:
    - s: Serie de pandas a clasificar.
    - threshold: umbral de cardinalidad para considerar una variable numérica como continua.
    """
    # Número de valores únicos (sin NaN)
    non_na = s.dropna()
    unique_count = int(non_na.nunique()) if not non_na.empty else 0

    # Si es numérico y tiene alta cardinalidad, lo consideramos continuo
    if pd.api.types.is_numeric_dtype(s):
        if unique_count > threshold:
            return 'numerico_continuo'
        if non_na.empty:
            return 'numerico_continuo'
        # Si todos los valores son enteros (o floats sin componente decimal), tratarlos como discretos
        if pd.api.types.is_integer_dtype(non_na):
            return 'numerico_discreto'
        vals = non_na.astype(float).to_numpy()
        if np.all(np.isclose(np.mod(vals, 1), 0)):
            return 'numerico_discreto'
        return 'numerico_continuo'
    else:
        # No es numérico: considerar categórico
        return 'categorico'

def crear_graficos_discretos(df, clasificaciones):
    """
    Guarda la información necesaria para graficar variables discretas,
    pero no muestra ningún gráfico por defecto.
    """
    # Diccionario para almacenar los datos de los gráficos
    graficos = {}

    # Obtener la lista de variables que han sido clasificadas como discretas
    discrete_vars = [d['variable'] for d in clasificaciones if d['classification'] == 'numerico_discreto']

    # Iterar sobre cada variable discreta
    for var in discrete_vars:
        # Eliminar valores nulos de la serie
        s = df[var].dropna()

        # Contar las ocurrencias de cada valor y ordenar por índice
        vc = s.value_counts().sort_index()
        
        # Guardar los datos del gráfico: tipo de gráfico, valores del eje X e Y
        graficos[var] = {
            'tipo': 'bar',
            'x': vc.index.astype(str),
            'y': vc.values
        }

    # Retornar el diccionario con la información de todos los gráficos
    return graficos

def mostrar_graficos_discretos(graficos, var=None, ncols=3, figsize=(18, 12)):
    """
    Muestra un gráfico individual si se pasa 'var',
    o todos los gráficos en una rejilla si no se pasa.
    """
    # Si se indica una variable concreta, se muestra solo su gráfico
    if var is not None:
        info = graficos[var]
        fig, ax = plt.subplots(figsize=(6, 4))

        # Dibuja el gráfico de barras con los datos de esa variable
        ax.bar(info['x'], info['y'])
        ax.set_ylabel('Conteos')

        # Etiquetas y título del gráfico
        ax.set_xlabel(var)
        ax.set_title(var)

        fig.tight_layout()
        plt.show()
        return

    # Si no se indica variable, se muestran todos los gráficos
    vars_ = list(graficos.keys())
    n = len(vars_)
    nrows = int(np.ceil(n / ncols))

    # Crea la rejilla de subgráficos
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.array(axes).reshape(-1)

    # Recorre todas las variables y pinta cada gráfico en su eje
    for i, v in enumerate(vars_):
        ax = axes[i]
        info = graficos[v]

        # Solo dibuja barras si el tipo de gráfico es 'bar'
        if info['tipo'] == 'bar':
            ax.bar(info['x'], info['y'])
            ax.set_ylabel('Conteos')

        # Configura etiquetas y título
        ax.set_xlabel(v)
        ax.set_title(v)

    # Elimina los ejes sobrantes si hay más subplots que gráficos
    for j in range(n, len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    plt.show()


def crear_graficos_continuos(df, clasificaciones):
    """
    Guarda la información necesaria para graficar variables continuas
    (histograma + KDE y boxplot) pero no muestra gráficos.
    """
    # Diccionario para almacenar la información de los gráficos
    graficos = {}

    # Extrae las variables clasificadas como continuas de la lista de clasificaciones
    cont_vars = [c['variable'] for c in clasificaciones if c['classification'] == 'numerico_continuo']

    # Itera sobre cada variable continua
    for var in cont_vars:
        # Obtiene la serie de datos sin valores faltantes
        s = df[var].dropna()
        
        # Si la serie está vacía, salta a la siguiente variable
        if s.empty:
            continue

        # Almacena la información del gráfico para esta variable
        graficos[var] = {
            'tipo': 'histograma_kde_boxplot',
            'data': s,
            'bins': 40,
            # Calcula estadísticas descriptivas de la variable
            'stats': {
                'media': float(s.mean()),
                'mediana': float(s.median()),
                'std': float(s.std()),
                'q1': float(s.quantile(0.25)),
                'q3': float(s.quantile(0.75)),
                'min': float(s.min()),
                'max': float(s.max())
            }
        }

    # Retorna el diccionario con toda la información de los gráficos
    return graficos



def mostrar_graficos_continuos(graficos, var=None, ncols=2, figsize=(10, 12), gridspec={'height_ratios': [3, 1]}):
    """
    Muestra un gráfico individual (histograma + KDE y boxplot) si se pasa 'var',
    o todos los gráficos en una rejilla si no se pasa.
    """
    # convertir las claves del diccionario a lista de variables
    vars_ = list(graficos.keys())

    # Si se especifica una variable, dibujar solo ese par de gráficos (histograma + boxplot)
    if var is not None:
        info = graficos[var]
        # crear figura con dos subplots apilados (histograma arriba, boxplot abajo)
        fig, (ax_hist, ax_box) = plt.subplots(2, 1, figsize=figsize, gridspec_kw=gridspec)
        # histograma con KDE
        sns.histplot(info['data'], bins=info.get('bins', 40), kde=True, ax=ax_hist, color='C0')
        ax_hist.set_ylabel('Densidad / Conteo')
        ax_hist.set_title(var)

        # boxplot horizontal
        sns.boxplot(x=info['data'], ax=ax_box, color='C1', orient='h')
        ax_box.set_xlabel(var)
        ax_box.set_yticks([])  # ocultar ticks del eje y porque no aportan información

        fig.tight_layout()
        plt.show()
        return

    # Si no hay variables, salir
    n = len(vars_)
    if n == 0:
        return

    # calcular filas necesarias (cada variable usa 2 filas: histograma + boxplot)
    nrows = int(np.ceil(n / ncols))
    nrows_grid = nrows * 2  # dos filas por variable en la cuadrícula
    fig, axes = plt.subplots(nrows_grid, ncols, figsize=figsize)
    # asegurar que 'axes' tenga forma (nrows_grid, ncols)
    axes = np.array(axes).reshape(nrows_grid, ncols)

    # iterar por cada variable y dibujar sus gráficos en la posición correspondiente
    for i, v in enumerate(vars_):
        r_block = (i // ncols) * 2  # fila superior del bloque de 2 filas para esta variable
        c = i % ncols              # columna en la que dibujar
        ax_hist = axes[r_block, c]
        ax_box = axes[r_block + 1, c]

        info = graficos[v]
        # histograma con KDE
        sns.histplot(info['data'], bins=info.get('bins', 40), kde=True, ax=ax_hist)
        ax_hist.set_title(v)
        ax_hist.set_ylabel('Densidad / Conteo')

        # boxplot horizontal debajo del histograma
        sns.boxplot(x=info['data'], ax=ax_box, color='C1', orient='h')
        ax_box.set_xlabel(v)
        ax_box.set_yticks([])

    # eliminar ejes sobrantes cuando el número de variables no llena la cuadrícula completa
    total_cells = nrows * ncols
    for j in range(n, total_cells):
        r_block = (j // ncols) * 2
        c = j % ncols
        fig.delaxes(axes[r_block, c])
        fig.delaxes(axes[r_block + 1, c])

    fig.tight_layout()
    plt.show()


def graficar_top_items(tablas, figsize=(18, 14), ncols=2, top_n=15):
    """
    Crea gráficos de barras horizontales para los top N items de cada tabla.
    
    Parámetros:
    -----------
    tablas : dict
        Diccionario con títulos como claves y series de pandas como valores
    figsize : tuple
        Tamaño de la figura (ancho, alto)
    ncols : int
        Número de columnas en la cuadrícula de subplots
    top_n : int
        Número de top items a mostrar (por defecto 15)
    """
    # Calcular número de filas necesarias en función de la cantidad de tablas y columnas
    nrows = (len(tablas) + ncols - 1) // ncols
    # Crear figura y ejes (subplots)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    # Aplanar el arreglo de ejes para iterar fácilmente (incluso si nrows*ncols > 1)
    axes = axes.flatten()
    
    # Obtener lista de pares (titulo, serie) para iterar
    items = list(tablas.items())
    
    # Iterar por cada eje y su correspondiente (titulo, serie)
    for ax, (titulo, serie) in zip(axes, items):
        # Eliminar valores nulos y asegurar tipo string (para conteos consistentes)
        serie = serie.dropna().astype(str)
        # Total de elementos en la serie (para calcular porcentajes)
        total = serie.shape[0]
        # Obtener los top N items por frecuencia y ordenarlos para la gráfica horizontal
        top_items = serie.value_counts().head(top_n).sort_values()
        # Definir paleta de colores según la cantidad de items a mostrar
        colors = sns.color_palette("viridis", n_colors=len(top_items))
        # Dibujar barra horizontal con seaborn; se usa 'hue' para colorear por índice pero sin leyenda
        sns.barplot(x=top_items.values, y=top_items.index, hue=top_items.index, palette=colors, ax=ax, legend=False)
        # Título y etiquetas
        ax.set_title(f"Top {top_n} de {titulo}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Frecuencia")
        ax.set_ylabel("")
        
        # Máxima anchura de barra (para posicionar etiquetas)
        max_width = top_items.values.max() if len(top_items) > 0 else 0
        # Añadir anotaciones con conteo y porcentaje dentro o fuera de la barra según tamaño
        for p in ax.patches:
            width = p.get_width()
            count = int(width)
            pct = width / total * 100 if total > 0 else 0
            # Si la barra es suficientemente ancha, colocar el texto centrado; si no, a la derecha
            if max_width > 0 and width >= max_width * 0.15:
                x = width / 2
                ha = "center"
            else:
                x = width + (max_width * 0.01 if max_width > 0 else 0.01)
                ha = "left"
            # Dibujar el texto con conteo y porcentaje
            ax.text(x, p.get_y() + p.get_height() / 2, f"{count} ({pct:.1f}%)", 
                   ha=ha, va="center", color="black", fontsize=9)
    
    # Ocultar subplots que no se utilizaron (si la cuadrícula es mayor que la cantidad de tablas)
    for idx in range(len(items), len(axes)):
        axes[idx].axis('off')
    
    # Ajustar layout y mostrar la figura
    plt.tight_layout()
    plt.show()

def clasificacion_agrupada(datos, categorias, tabla1, tabla2, type="mean"):
    """Agrupa y resume valoraciones por categorías y/o atributos asociados.

    Esta función fusiona dos tablas intermedias (`tabla1`, `tabla2`) con la tabla
    principal `datos` para calcular, por cada combinación (tabla1.col, tabla2.col),
    una medida resumen (media de `bayes_average` o conteo de apariciones).

    Parámetros:
    - datos: DataFrame principal que contiene al menos las columnas `bgg_id` y `bayes_average`.
    - categorias: lista de categorías a filtrar en `tabla1`.
    - tabla1: DataFrame con una columna (además de `bgg_id`) que representa la agrupación principal.
    - tabla2: DataFrame con una columna (además de `bgg_id`) que representa la agrupación secundaria.
    - type: 'mean' para calcular la media de `bayes_average`, 'count' para contar apariciones.

    Devuelve:
    - DataFrame con la métrica agregada por combinación de valores y el mejor resultado por grupo.
    """
    # Unir tabla1 y tabla2 por la columna 'bgg_id' para obtener combinaciones de ambas tablas
    df_merge = tabla1.merge(tabla2, on='bgg_id', how='left')

    # Filtrar las filas donde la columna de agrupación principal (segunda columna de tabla1)
    # está dentro de la lista de categorías proporcionada
    df_filt = df_merge[df_merge[tabla1.columns[1]].isin(categorias)]

    # Añadir la columna 'bayes_average' desde la tabla principal 'datos' usando 'bgg_id'
    df_merge2 = df_filt.merge(datos[['bgg_id','bayes_average']], on='bgg_id', how='left')

    if type == "mean":
        # Agrupar por la columna de tabla1 y la columna de tabla2 y calcular la media de 'bayes_average'
        ranking = (
            df_merge2
            .groupby([tabla1.columns[1], tabla2.columns[1]])["bayes_average"]
            .mean()
            .reset_index()
        )
        # Para cada valor de la columna de tabla1, obtener la fila con la media máxima de 'bayes_average'
        best_result = ranking.loc[ranking.groupby(tabla1.columns[1])["bayes_average"].idxmax()]
    elif type == "count":
        # Agrupar por la columna de tabla1 y la columna de tabla2 y contar ocurrencias de 'bgg_id'
        ranking = (
            df_merge2
            .groupby([tabla1.columns[1], tabla2.columns[1]])["bgg_id"]
            .count()
            .reset_index()
        )
        # Para cada valor de la columna de tabla1, obtener la fila con el mayor conteo
        best_result = ranking.loc[ranking.groupby(tabla1.columns[1])["bgg_id"].idxmax()]
    else:
        # Error si el tipo no es válido
        raise ValueError("type debe ser 'mean' o 'count'.")

    # Ordenar el resultado final por la columna de agrupación principal y devolverlo
    best_result = best_result.sort_values(tabla1.columns[1])
    return best_result


def pairplot_simetrico(tabla, columnas=None, hue=None, sample=None, dropna=True,
                       diag_kind='hist', corner=False, palette='Set2',
                       height=2.2, plot_kws=None, diag_kws=None):
    """
    Genera un pairplot evitando la matriz completa (solo un triángulo) para mayor rapidez.
    """
    # Si no se especifican columnas, usar todas las columnas del DataFrame
    if columnas is None:
        columnas = tabla.columns.tolist()

    # Evitar incluir la variable de hue dentro de las variables a plotear
    if hue in columnas:
        columnas = [c for c in columnas if c != hue]

    # Filtrar solo las columnas numéricas, porque pairplot necesita ejes numéricos
    columnas_numericas = [c for c in columnas if pd.api.types.is_numeric_dtype(tabla[c])]
    # Registrar las columnas que se omiten por no ser numéricas
    columnas_omitidas = [c for c in columnas if c not in columnas_numericas]

    # Si no quedan columnas numéricas, no tiene sentido crear el pairplot
    if not columnas_numericas:
        raise ValueError("No hay columnas numéricas para representar en el pairplot.")

    # Preparar el DataFrame para el plot, añadiendo hue si procede
    cols_plot = columnas_numericas + ([hue] if hue is not None else [])
    df_plot = tabla[cols_plot].copy()

    # Opción para eliminar filas con NA antes de plotear
    if dropna:
        df_plot = df_plot.dropna()

    # Si se pide una muestra, reducir el DataFrame para acelerar el gráfico
    if sample is not None and len(df_plot) > sample:
        df_plot = df_plot.sample(sample, random_state=42)

    # Valores por defecto para parámetros de los plots si no se proporcionan
    if plot_kws is None:
        plot_kws = {"alpha": 0.5, "s": 18}
    if diag_kws is None:
        diag_kws = {"bins": 25}

    # Crear el pairplot con seaborn usando solo el triángulo (corner) si se desea
    g = sns.pairplot(
        data=df_plot,
        vars=columnas_numericas,
        hue=hue,
        corner=corner,  # usar solo un triángulo para acelerar
        diag_kind=diag_kind,
        palette=palette,
        height=height,
        plot_kws=plot_kws,
        diag_kws=diag_kws
    )

    # Añadir un título informativo al figure
    titulo = f"Pairplot ({len(columnas_numericas)} variables)"
    if sample is not None:
        titulo += f" - muestra={len(df_plot)}"
    g.figure.suptitle(titulo, y=1.02)

    # Informar de las columnas omitidas por no ser numéricas
    if columnas_omitidas:
        print("Columnas omitidas (no numéricas):", columnas_omitidas)

    return g