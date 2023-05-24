import streamlit as st

import pandas as pd
import numpy as np


import plotly.express as px
import plotly.graph_objects as go


st.set_page_config(
    page_title="Dashboard interactivo", # cambia el título de la página
    page_icon=":airplane:", # cambia el icono de la página
    layout="wide", # usa el ancho completo de la pantalla
    initial_sidebar_state="expanded", # muestra el sidebar inicialmente
)


@st.cache_data
def get_df():
    return pd.read_csv('../data/transform/asn_final_v3.csv')


@st.cache_data
def get_pais(dataframe):
    return dataframe.pais_accidente.str.title().sort_values(ascending=True).unique()


@st.cache_data
def get_continent(dataframe):
    return dataframe.continente.str.title().sort_values(ascending=True).unique()


def filter_by_date(dataframe, initial_date, final_date):
    initial_date, final_date = str(initial_date), str(final_date)
    return dataframe[(dataframe.fecha >= initial_date) & (dataframe.fecha <= final_date)]


def filter_by_dict(dataframe, filtrate):
    for col, value in filtrate.items():
        if isinstance(value, list):
            value = [v.lower() for v in value]
            indice = dataframe[col].isin(value)
            dataframe = dataframe[indice]
        else:
            value = value.lower()
            dataframe = dataframe[dataframe[col] == value]
    return dataframe


def compute_1_kpi(dataframe, dataframe_filtrado, label):
    """La tasa de mortalidad mide el numero de fallecidos respecto del total de accidentes."""

    general = dataframe.total_fallecidos.sum() / dataframe.shape[0]
    value = dataframe_filtrado.total_fallecidos.sum() / dataframe_filtrado.shape[0]
    delta = value - general

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=value, delta=delta)


def compute_2_kpi(dataframe, dataframe_filtrado, label):
    """Mide el numero de accidentes que involucraron pasajeros respecto del total de accidentes."""

    general = dataframe[dataframe.cant_pasajeros > 0].shape[0] / dataframe.shape[0]
    value = dataframe_filtrado[dataframe_filtrado.cant_pasajeros > 0].shape[0] / dataframe_filtrado.shape[0]
    delta = value - general

    value, delta = [f'{x * 100:.1f} %' for x in [value, delta]]
    return dict(label=label, value=value, delta=delta)


def compute_3_kpi(dataframe, dataframe_filtrado, label):
    """Tasa de variacion: mide el valor medio de variacion del numero de accidentes de año a año."""

    general = (dataframe.year.value_counts() - dataframe.year.value_counts().shift(-1)).mean()
    value = (dataframe_filtrado.year.value_counts() - dataframe_filtrado.year.value_counts().shift(-1)).mean()
    delta = value - general

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=value, delta=delta)


def compute_4_kpi(dataframe, dataframe_filtrado, label):
    """Variacion anual ponderada: el numero de accidentes esta ponderado por la
    ratio entre fallecidos y vivos en ese año y sobre ello se calcula la diferencia"""

    metrics = []
    for data in [dataframe, dataframe_filtrado]:

        fallecidos = data.groupby('year').total_fallecidos.sum()
        vivos = data.groupby('year').total_vivos.sum()
        cantidad_accidentes = data.groupby('year').total_fallecidos.count()

        ratio = (fallecidos / vivos).replace([np.inf, -np.inf], 0) * cantidad_accidentes

        metrics.append((ratio - ratio.shift(-1)).mean())

    # Calculamos delta
    metrics[1] = metrics[0] - metrics[1]
    value, delta = [round(x, 2) for x in metrics]
    return dict(label=label, value=value, delta=delta)


def compute_5_kpi(dataframe, dataframe_filtrado, label):
    """Distancia temporal media: computa el numero de dias medios entre accidente y accidente.
       De otro modo, es una medida de frecuencia de accidentes. """

    general = (dataframe.shift(-1).fecha - dataframe.fecha).dt.days.mean()
    value = (dataframe_filtrado.shift(-1).fecha - dataframe_filtrado.fecha).dt.days.mean()
    delta = value - general

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=value, delta=delta)

def compute_kpis(dataframe, dataframe_filtrado, labels, num_kpis):
    output = []
    kpi_func = [compute_1_kpi, compute_2_kpi, compute_3_kpi, compute_4_kpi, compute_5_kpi]

    for i in range(num_kpis):
        func = kpi_func[i]
        output.append(func(dataframe, dataframe_filtrado, labels[i]))

    return output


# CARGA LOS DATOS
original = get_df()
original.fecha = pd.to_datetime(original.fecha)
mindate, maxdate = original.fecha.min(), original.fecha.max()

paises = get_pais(original)
continentes = get_continent(original)

df = original.copy()


st.markdown("<h1 style='text-align: center; color: grey;'>EVOLUCION Y ACTUALIDAD DE LOS ACCIDENTES AEREOS</h1>", unsafe_allow_html=True)
st.markdown('')

# FILTRAR POR PAIS O CONTINENTE
st.markdown("<h3 style='text-align: left; color: grey;'>FILTRO PRINCIPAL</h1>", unsafe_allow_html=True)
which_filter = st.radio('Quieres filtrar por:', ('Pais', 'Continente', 'No filtrar'), )

if which_filter == 'Pais':
    pais = st.selectbox('Selecciona el pais/zona:', paises)
    filtrar = dict(pais_accidente=pais)
elif which_filter == 'Continente':
    continente = st.selectbox('Selecciona el continente:', continentes)
    filtrar = dict(continente=continente)
else:
    filtrar = {}

# OTROS FILTROS

# FILTRO POR FECHA
st.markdown("<h3 style='text-align: left; color: grey;'>Rango de fechas</h1>", unsafe_allow_html=True)
date_cols = st.columns(2)
initial_date = date_cols[0].date_input('Fecha de inicio: ',
                            min_value=mindate, max_value=maxdate, value=mindate)

final_date = date_cols[1].date_input('Fecha final: ',
                            min_value=mindate, max_value=maxdate, value=maxdate)

df = filter_by_date(df, initial_date, final_date)

# FILTRO POR TIPO DE DAÑO FINAL DE LA AERONAVE
aircraft_damage = st.multiselect('Filtrar por daño final de la aeronave:',
                                 df.aircraft_damage.str.title().sort_values(ascending=True).unique(),
                                 df.aircraft_damage.str.title().sort_values(ascending=True).unique())
if aircraft_damage:
    filtrar['aircraft_damage'] = aircraft_damage

st.divider()

st.markdown("<h3 style='text-align: left; color: grey;'>KPIs</h1>", unsafe_allow_html=True)

# CONSTRUYE, COMPUTA Y GRAFICA LOS KPIS
num_kpis = 5
kpis_cols = st.columns(num_kpis)
kpis_label = ['Tasa de mortalidad', 'Sensibilidad de pasajeros',
              'Media de variacion anual', 'Variacion anual ponderada',
              'Distancia temporal media']

dataframe_filtrado = filter_by_dict(df, filtrar)
kpis_outputs = compute_kpis(df, dataframe_filtrado, kpis_label, num_kpis)

for i in range(num_kpis):
    kpi = kpis_cols[i]
    kpi.metric(**kpis_outputs[i])


# PRIMERA FILA DE GRAFICOS

st.divider()

# PRIMER GRAFICO

width, height = 600, 450

graph_cols = st.columns(2)

fig = go.Figure()
fig.add_trace(go.Scatter(x=dataframe_filtrado.groupby('year').victimas.sum().index,
                         y=dataframe_filtrado.groupby('year').victimas.sum(),
                         mode='lines',
                         name='Accidentes con victimas fatales',
                         line=dict(color='rgba(255, 0, 0, 0.5)', width=3)))
fig.add_trace(go.Scatter(x=dataframe_filtrado.groupby('year').fecha.count().index,
                         y=dataframe_filtrado.groupby('year').fecha.count(),
                         mode='lines',
                         name='Cantidad de accidentes',
                         line=dict(color='rgba(0, 0, 255, 0.5)', width=3)))

fig.update_layout(
    title=dict(text="Accidentes [con vs sin] victimas fatales", font=dict(size=24), automargin=True, yref='paper'),
    legend=dict(orientation='v', yanchor='top', y=1.0, xanchor='left', x=0, font=dict(size=14)),
    width=width, height=height,
)

graph_cols[0].plotly_chart(fig)

with graph_cols[0].expander('Explicacion'):
    st.write('Se grafican dos lines plots que corresponden a:')
    st.write('1. Numero totales de accidentes que involucran al menos una muerte por año (rojo)')
    st.write('2. Numero total de accidentes por año (azul).')


# SEGUNDO GRAFICO

colors = ['gold', 'mediumturquoise', 'darkorange', 'lightgreen', 'lightgrey']

# Obtén los valores y nombres del DataFrame
valores = dataframe_filtrado['razon'].value_counts().sort_values(ascending=True).tail(5).values
nombres = dataframe_filtrado['razon'].value_counts().sort_values(ascending=True).tail(5).index

# Crea el gráfico de pastel con valores y nombres
fig = px.pie(values=valores, names=nombres)

fig.update_traces(hoverinfo='label+percent', textinfo='value', textfont_size=20,
                  marker=dict(colors=colors, line=dict(color='#000000', width=2)))

fig.update_layout(
    title=dict(text="Top 5 razones de vuelo", font=dict(size=24), automargin=True, yref='paper'),
    legend=dict(orientation='v', yanchor='top', y=1.0, xanchor='right', x=0, font=dict(size=14)),
    width=width, height=height,
)

graph_cols[1].markdown('')
graph_cols[1].plotly_chart(fig)

# SEGUNDA FILA DE GRAFICOS

graph_cols = st.columns(2)

# TERCER GRAFICO

group_tf = dataframe_filtrado.groupby('year').total_fallecidos.sum()
group_tv = dataframe_filtrado.groupby('year').total_vivos.sum()
result = group_tf / group_tv
color = np.where(result >= 1, 'Mayor numero de fallecidos', 'Mayor numero de sobrevientes')
color_map = {'Mayor numero de fallecidos': 'rgba(200, 0, 0, 0.5)', 'Mayor numero de sobrevientes': 'rgba(0, 150, 0, 0.5)'}

fig = px.bar(x=result.index, y=result.values, color=color, color_discrete_map=color_map)
fig.update_layout(
    title=dict(text="Ratio fallecidos/sobrevivientes por año", font=dict(size=24), automargin=True, yref='paper'),
    legend=dict(orientation='v', yanchor='top', y=1.0, xanchor='left', x=0, font=dict(size=14)),
    width=width, height=height,
)

graph_cols[0].plotly_chart(fig)

with graph_cols[0].expander('Explicacion'):
    st.write('Se grafica el ratio de total_fallecidos / total_vivos')
    st.write('El color verde corresponde a casos en que el ratio es menor que 0, o lo que es lo mismo '
             'cuando el numero de sobrevivientes es mayor que el de fallecidos. De manera inversa, el color es rojo '
             'cuando fallecieron mas personas de las que sobrevivieron.')



# CUARTO GRAFICO

graph_cols[1].markdown('#### **Metricas**')

def compute_1_metric(dataframe, dataframe_filtrado, label):
    """Accidentes totales"""
    general = dataframe.shape[0]
    value = dataframe_filtrado.shape[0]
    delta = value / general * 100

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=f'{value} ({delta}%)')

def compute_2_metric(dataframe, dataframe_filtrado, label):
    """Fallecidos totales"""

    general = dataframe.total_fallecidos.sum()
    value = dataframe_filtrado.total_fallecidos.sum()
    delta = value / general * 100

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=f'{value} ({delta}%)')


def compute_3_metric(dataframe, dataframe_filtrado, label):
    """Numero de accidentes que involucraron al menos una muerte"""

    dataframe = dataframe[dataframe.victimas == True]
    dataframe_filtrado = dataframe_filtrado[dataframe_filtrado.victimas == True]

    general = dataframe.shape[0]
    value = dataframe_filtrado.shape[0]
    delta = value / general * 100

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=f'{value} ({delta}%)')


def compute_4_metric(dataframe, dataframe_filtrado, label):
    """Promedio de edad de los aviones accidentados"""

    general = dataframe['edad_avion'].mean()
    value = dataframe_filtrado['edad_avion'].mean()
    delta = (value - general) / general * 100

    value, delta = [round(x, 2) for x in [value, delta]]
    return dict(label=label, value=f'{value} ({delta}%)')


def compute_metrics(dataframe, dataframe_filtrado, num_metrics, labels):
    output = []
    func_metrics = [compute_1_metric, compute_2_metric, compute_3_metric, compute_4_metric]
    for i in range(num_metrics):
        func = func_metrics[i]
        label = labels[i]
        output.append(func(dataframe, dataframe_filtrado, label))
    return output


col1, col2 = graph_cols[1].columns(2)
graph_cols[1].columns(2)
graph_cols[1].columns(2)
col3, col4 = graph_cols[1].columns(2)
metric_cols = [col1, col2, col3, col4]

# CONSTRUYE, COMPUTA Y GRAFICA LOS KPIS
num_metrics = 4
metrics_label = ['Accidentes totales', 'Fallecidos totales',
                 'Num. accidentes con victimas.', 'Edad media de los aviones accidentados']
metric_outputs = compute_metrics(df, dataframe_filtrado, num_metrics, metrics_label)
for i in range(num_metrics):
    col = metric_cols[i]
    output = metric_outputs[i]
    col.metric(**output)

st.divider()

# MAPA MUNDIAL

st.markdown("<h3 style='text-align: left; color: grey;'>MAPA MUNDIAL</h1>", unsafe_allow_html=True)
st.write('Se visualiza cada pais involucrado en un accidente y se lo grafica '
         'segun su cantidad de accidentes o de fallecidos.')

#which_filter

@st.cache_data
def geo_plot(dataframe, year, by_country, by_accident):

    dataframe = dataframe[dataframe.year < year]

    if by_country:
        var = 'pais_accidente'
        lat, lon = 'lat', 'lon'
    else:
        var = 'continente'
        lat, lon = 'lat_cont', 'lon_cont'

    if by_accident:
        dataframe['freq'] = dataframe.groupby(var)[var].transform("count")
    else:
        dataframe['freq'] = dataframe.groupby(var)['total_fallecidos'].transform("sum")

    fig = px.scatter_geo(
        dataframe,
        lat=lat,
        lon=lon,
        color=var,
        size='freq',
        hover_name=var,
        projection="natural earth",
        size_max=30,
        opacity=0.5
    )

    return fig


def format_options(option):
    if option == True:
        return 'Num. Accidentes'
    return 'Cant. Fallecidos'


min_year, max_year = [int(x) for x in [df.year.min(), df.year.max()]]
value_year = st.slider('Rango de años:', min_value=min_year, max_value=max_year, value=max_year)
value_accident = st.radio('Mostrar segun el numero de accidentes o cantidad de fallecidos?',
                              [True, False], format_func=format_options)

if which_filter == 'Pais':
    fig = geo_plot(original, value_year, True, value_accident)
else:
    fig = geo_plot(original, value_year, False, value_accident)

st.plotly_chart(fig, use_container_width=True)






