import streamlit as st


st.set_page_config(
    page_title="Introduccion", # cambia el título de la página
    page_icon=":airplane:", # cambia el icono de la página
    layout="wide", # usa el ancho completo de la pantalla
    initial_sidebar_state="expanded", # muestra el sidebar inicialmente
)


st.markdown("<h1 style='text-align: center; color: grey;'>Data Analysis: Aviation Safety Network</h1>", unsafe_allow_html=True)
st.markdown('')

st.divider()
st.markdown('## Introduccion')

'Este pagina web diseñada en streamlit es parte del proyecto numero 2 de la etapa ' \
'labs del bootcamp de SoyHenry.'

'A su izquierda encontraran dos paginas, incluyendo la actual (Home).'

'La pagina "Dashboard" contiene el dashboard interactivo en el que usted podra estudiar distintas metricas ' \
'segun el pais, continente o a nivel general.'

'Home es una descripcion general sobre el dataset utilizado en el dashboard, definicion de KPIS y, ' \
'a su vez, contendra un breve resumen analitico, basado en los hallazgos encontrados.'

st.divider()
st.markdown('## Descripcion del dataset')
st.write('El dataset fue extraido de la base de datos de Aviation Safety Network.'
         'La Red de Seguridad de Aviación (ASN) es una fuente privada e independiente de información precisa y autorizada sobre accidentes aéreos y problemas de seguridad. '
         'Está respaldada por la Fundación para la Seguridad del Vuelo.')

st.write('La base de datos se puede encontrar en: https://aviation-safety.net/database/')

st.write(
    'El scraper junto con la "raw data" que se extrajo se puede encontrar en: https://github.com/jcamatta/aviation_safety_network_data')

st.write('La base de datos paso por distintos procesos de transformacion, resultando en un conjunto conformado '
         'por 39 columnas y 19253 registros. La ventana temporal es desde 1919 hasta 2022.')

st.divider()
st.markdown('## Descripcion de KPIS.')

st.markdown('#### 1. Primer KPI: Tasa de Mortalidad.')
st.write('La tasa de mortalidad mide el numero de fallecidos respecto del total de accidentes. '
         'Por lo que nos permite estudiar la gravedad de los accidentes.')

st.latex('Tasa \\ de \\ mortalidad = \\frac{fallecidos}{accidentes}')

st.markdown('#### 2. Segundo KPI: Sensibilidad de pasajeros.')
st.write('Este KPI tiene en cuenta el numero de accidentes que involucran al menos 1 pasajero.'
         ' La razon del mismo, es que vuelos de otro caracter, como los militares, si bien igual de importantes,'
         ' involucran menos personas y a la vez contienen una complejidad y peligrosidad mayor.')

st.latex('Sensibilidad \\ de \\ pasajeros = \\frac{con \\ pasajeros}{accidentes} * 100')

st.markdown('#### 3. Tercer KPI: Variacion anual media.')
st.write('Como sabemos si nuestros esfuerzos estan haciendo efectos? Una forma seria estudiar el numero de accidentes '
         'por año y compararlo con el anterior. Esto es lo que computa este KPI, calcula la diferencia año a año y al '
         'resultado le computa la media.')

st.latex('Variacion \\ anual \\ media = Mean(accidentes \\times (t) - accidentes \\times (t-1))')

st.markdown('#### 4. Cuarto KPI: Variacion anual ponderada.')
st.write('La gravedad de un accidente se mide principalmente por la cantidad de muertes que implica. '
         'Por lo que cada numero de accidentes se ponderada a su vez por '
         'el ratio entre fallecidos y sobrevivientes/vivos de ese año, luego se calcula la diferencia. '
         'Un año que involucro menos accidentes pero quizas mas '
         'muertes puede tener mayor peso que otro. De mismo modo, aquel año que tuvo 0 muertes, no afecta al KPI. '
         'Lo que busca este KPI es involucrar los dos valores mas importantes, a saber: accidentes y fallecidos.')

st.latex('Variacion \\ anual \\ ponderada = Mean(r (t) \\times accidentes \\times (t) - r (t - 1) \\times accidentes \\times (t-1))')

st.markdown('*donde r es la funcion que calcula el ratio entre las columnas total_fallecidos y total_vivos.*')

st.markdown('#### 5. Quinto KPI: Distancia temporal media.')
st.write('Por ultimo, el quinto KPI nos permitira evaluar si la frecuencia de accidentes aumenta o no. Se calcula como '
         'el valor medio de distancia de dias entre accidentes. Por lo que un mayor valor es deseable.')

st.latex('Distancia \\ temporal \\ media = Mean(Dia(accidente(t)) - Dia(accidente(t-1)))')

st.divider()