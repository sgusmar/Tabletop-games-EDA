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
    # Determinar número de valores únicos (sin contar NaN)
    non_na = s.dropna()
    unique_count = int(non_na.nunique()) if not non_na.empty else 0

    # Si es numérico y alta cardinalidad (más de threshold valores únicos), forzar continuo
    if pd.api.types.is_numeric_dtype(s):
        if unique_count > threshold:
            return 'numerico_continuo'
        if non_na.empty:
            return 'numerico_continuo'
        # Entero nativo
        if pd.api.types.is_integer_dtype(non_na):
            return 'numerico_discreto'
        # Float pero con valores enteros (ej. ranks 1.0, 2.0) -> discreto
        vals = non_na.astype(float).to_numpy()
        if np.all(np.isclose(np.mod(vals, 1), 0)):
            return 'numerico_discreto'
        return 'numerico_continuo'
    else:
        return 'categorico'

def crear_graficos_discretos(df, clasificaciones):
    """
    Guarda la información necesaria para graficar variables discretas,
    pero no muestra ningún gráfico por defecto.
    """
    graficos = {}

    discrete_vars = [d['variable'] for d in clasificaciones if d['classification'] == 'numerico_discreto']

    for var in discrete_vars:
        s = df[var].dropna()

        vc = s.value_counts().sort_index()
        graficos[var] = {
            'tipo': 'bar',
            'x': vc.index.astype(str),
            'y': vc.values
        }

    return graficos

def mostrar_graficos_discretos(graficos, var=None, ncols=3, figsize=(18, 12)):
    """
    Muestra un gráfico individual si se pasa 'var',
    o todos los gráficos en una rejilla si no se pasa.
    """
    if var is not None:
        info = graficos[var]
        fig, ax = plt.subplots(figsize=(6, 4))
  
        ax.bar(info['x'], info['y'])
        ax.set_ylabel('Conteos')

        ax.set_xlabel(var)
        ax.set_title(var)
        fig.tight_layout()
        plt.show()
        return

    vars_ = list(graficos.keys())
    n = len(vars_)
    nrows = int(np.ceil(n / ncols))

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = np.array(axes).reshape(-1)

    for i, v in enumerate(vars_):
        ax = axes[i]
        info = graficos[v]

        if info['tipo'] == 'bar':
            ax.bar(info['x'], info['y'])
            ax.set_ylabel('Conteos')

        ax.set_xlabel(v)
        ax.set_title(v)

    for j in range(n, len(axes)):
        fig.delaxes(axes[j])

    fig.tight_layout()
    plt.show()

def crear_graficos_continuos(df, clasificaciones):
    """
    Guarda la información necesaria para graficar variables continuas
    (histograma + KDE y boxplot) pero no muestra gráficos.
    """
    graficos = {}

    cont_vars = [c['variable'] for c in clasificaciones if c['classification'] == 'numerico_continuo']

    for var in cont_vars:
        s = df[var].dropna()
        if s.empty:
            continue

        graficos[var] = {
            'tipo': 'histograma_kde_boxplot',
            'data': s,
            'bins': 40,
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

    return graficos



def mostrar_graficos_continuos(graficos, var=None, ncols=2, figsize=(10, 12), gridspec={'height_ratios': [3, 1]}):
    """
    Muestra un gráfico individual (histograma + KDE y boxplot) si se pasa 'var',
    o todos los gráficos en una rejilla si no se pasa.
    """
    vars_ = list(graficos.keys())
    if var is not None:
        info = graficos[var]
        fig, (ax_hist, ax_box) = plt.subplots(2, 1, figsize=figsize, gridspec_kw=gridspec)
        sns.histplot(info['data'], bins=info.get('bins', 40), kde=True, ax=ax_hist, color='C0')
        ax_hist.set_ylabel('Densidad / Conteo')
        ax_hist.set_title(var)

        sns.boxplot(x=info['data'], ax=ax_box, color='C1', orient='h')
        ax_box.set_xlabel(var)
        ax_box.set_yticks([])

        fig.tight_layout()
        plt.show()
        return

    n = len(vars_)
    if n == 0:
        return

    nrows = int(np.ceil(n / ncols))
    nrows_grid = nrows * 2  # two rows per variable (hist + box)
    fig, axes = plt.subplots(nrows_grid, ncols, figsize=figsize)
    axes = np.array(axes).reshape(nrows_grid, ncols)

    for i, v in enumerate(vars_):
        r_block = (i // ncols) * 2
        c = i % ncols
        ax_hist = axes[r_block, c]
        ax_box = axes[r_block + 1, c]

        info = graficos[v]
        sns.histplot(info['data'], bins=info.get('bins', 40), kde=True, ax=ax_hist)
        ax_hist.set_title(v)
        ax_hist.set_ylabel('Densidad / Conteo')

        sns.boxplot(x=info['data'], ax=ax_box, color='C1', orient='h')
        ax_box.set_xlabel(v)
        ax_box.set_yticks([])

    # eliminar ejes sobrantes
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
    nrows = (len(tablas) + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)
    axes = axes.flatten()
    
    items = list(tablas.items())
    
    for ax, (titulo, serie) in zip(axes, items):
        serie = serie.dropna().astype(str)
        total = serie.shape[0]
        top_items = serie.value_counts().head(top_n).sort_values()
        colors = sns.color_palette("viridis", n_colors=len(top_items))
        sns.barplot(x=top_items.values, y=top_items.index, hue=top_items.index, palette=colors, ax=ax, legend=False)
        ax.set_title(f"Top {top_n} de {titulo}", fontsize=12, fontweight='bold')
        ax.set_xlabel("Frecuencia")
        ax.set_ylabel("")
        
        max_width = top_items.values.max() if len(top_items) > 0 else 0
        for p in ax.patches:
            width = p.get_width()
            count = int(width)
            pct = width / total * 100 if total > 0 else 0
            if max_width > 0 and width >= max_width * 0.15:
                x = width / 2
                ha = "center"
            else:
                x = width + (max_width * 0.01 if max_width > 0 else 0.01)
                ha = "left"
            ax.text(x, p.get_y() + p.get_height() / 2, f"{count} ({pct:.1f}%)", 
                   ha=ha, va="center", color="black", fontsize=9)
    
    # Ocultar subplots vacíos
    for idx in range(len(items), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    plt.show()

def clasificacion_agrupada(datos,categorias,tabla1,tabla2, type="mean"):
    df_merge = tabla1.merge(tabla2, on='bgg_id', how='left')
    df_filt = df_merge[df_merge[tabla1.columns[1]].isin(categorias)]
    df_merge2 = df_filt.merge(datos[['bgg_id','bayes_average']], on='bgg_id', how='left')
    if type == "mean":
        ranking = (
            df_merge2
            .groupby([tabla1.columns[1], tabla2.columns[1]])["bayes_average"]
            .mean()
            .reset_index()
        )
        best_result = ranking.loc[
        ranking.groupby(tabla1.columns[1])["bayes_average"].idxmax()
    ]
        
    elif type == "count":
        ranking = (
            df_merge2
            .groupby([tabla1.columns[1], tabla2.columns[1]])["bgg_id"]
            .count()
            .reset_index()
        )
        best_result = ranking.loc[
        ranking.groupby(tabla1.columns[1])["bgg_id"].idxmax()
    ]

    best_result.sort_values(tabla1.columns[1])
    return best_result


def pairplot_simetrico(tabla, columnas=None, hue=None, sample=None, dropna=True,
                       diag_kind='hist', corner=False, palette='Set2',
                       height=2.2, plot_kws=None, diag_kws=None):
    """
    Genera un pairplot evitando la matriz completa (solo un triángulo) para mayor rapidez.
    """
    if columnas is None:
        columnas = tabla.columns.tolist()

    # Evitar incluir la variable de hue dentro de vars
    if hue in columnas:
        columnas = [c for c in columnas if c != hue]

    # Pairplot solo admite variables numéricas en ejes
    columnas_numericas = [c for c in columnas if pd.api.types.is_numeric_dtype(tabla[c])]
    columnas_omitidas = [c for c in columnas if c not in columnas_numericas]

    if not columnas_numericas:
        raise ValueError("No hay columnas numéricas para representar en el pairplot.")

    cols_plot = columnas_numericas + ([hue] if hue is not None else [])
    df_plot = tabla[cols_plot].copy()

    if dropna:
        df_plot = df_plot.dropna()

    if sample is not None and len(df_plot) > sample:
        df_plot = df_plot.sample(sample, random_state=42)

    if plot_kws is None:
        plot_kws = {"alpha": 0.5, "s": 18}
    if diag_kws is None:
        diag_kws = {"bins": 25}

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

    titulo = f"Pairplot ({len(columnas_numericas)} variables)"
    if sample is not None:
        titulo += f" - muestra={len(df_plot)}"
    g.figure.suptitle(titulo, y=1.02)

    if columnas_omitidas:
        print("Columnas omitidas (no numéricas):", columnas_omitidas)

    return g

def subplot_pairplot(df, xlabel, ylabel, color_graf, **params_grafico):
    fig2, ax2 = plt.subplots(figsize=(8, 6))

    if xlabel == ylabel:
        sns.kdeplot(
            data=df,
            x=xlabel,
            hue=color_graf,
            fill=True,
            common_norm=True,
            ax=ax2,
            legend=True,
            **params_grafico
        )
    else:
        sns.scatterplot(
            data=df,
            x=xlabel,
            y=ylabel,
            hue=color_graf,
            ax=ax2,
            legend=True,
            **params_grafico
        )

    handles, labels = ax2.get_legend_handles_labels()
    if handles:
        ax2.legend(handles=handles, labels=labels, markerscale=1.5, title=str(color_graf), loc='best')

    fig2.tight_layout()
    plt.show()