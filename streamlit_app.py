import streamlit as st
import pandas as pd
import requests
import plotly.express as px
from streamlit_extras.mention import mention

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Usuario", on_change=password_entered, key="username")
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Usuario", on_change=password_entered, key="username")
        st.text_input(
            "Contraseña", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 Usuario desconocido o contraseña incorrecta")
        return False
    else:
        # Password correct.
        return True

if check_password():
    
    st.set_page_config(page_title="App IoT FIWARE",
                       page_icon="chart_with_upwards_trend", 
                       layout="wide")
    
    # Logos del proyecto
    st.sidebar.image("https://quesandaluz.es/wp-content/uploads/2023/01/Aristeo-V5-ok.jpg", 
                     use_column_width=True)
    
    st.sidebar.image("https://quesandaluz.es/wp-content/uploads/2023/01/Composici%C3%B3n-web.jpg", 
                     use_column_width=True)
    
    # Fiware STH: Quantum
    quantum_server = 'atdfiware.grayhats.com'
    quantum_endpoint = '/quantum/v2'
    
    # Fiware Structure Service
    fiwareservice = 'smarttrebol'
    fiwareservicepath = '/rabanales'
    
    
    # Título de la aplicación
    st.title('Aplicación para visualizar y descargar datos FIWARE')
    
    st.markdown("""---""")
    
    # Crear dos filas
    row1 = st.columns([1, 1, 1, 1])  # Tres columnas en la fila de arriba
    
    st.markdown("""---""")
    
    row2 = st.columns([1, 1])  # Dos columnas en la fila de abajo
    
    
    # Crear una función para formatear la fecha
    def format_date(selected_date):
        formatted_date = selected_date.strftime("%Y-%m-%dT%H:%M:%S.%f")
        return formatted_date
    
    
    # Crear un date_input en Streamlit
    fecha_inicio = st.sidebar.date_input("Seleccione una fecha de inicio", value = 'today')
    fecha_fin = st.sidebar.date_input("Seleccione una fecha fin", value = 'today')
    
    formatted_inicio = format_date(fecha_inicio)
    formatted_fin = format_date(fecha_fin)
    
    # URL y conexion al servidor
    accion = '/entities/urn:ngsi-ld:atdnoise:atd-noise-000/value?fromDate='+formatted_inicio+'&toDate='+formatted_fin
    url = 'https://'+quantum_server+quantum_endpoint+accion
    
    payload={}
    headers = {
      'Fiware-Service': fiwareservice,
      'Fiware-ServicePath': fiwareservicepath
    }
    
    
    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        
        if response.status_code == 200:
            print('El servidor no está disponible')
    except ValueError:
        st.error('El servidor no está disponible')
        
    
    try:
        json_data = response.json()
        lst = json_data['data']['attributes'][1]['values']
        lst2 = json_data['data']['attributes'][4]['values']
    
    except ValueError:
        st.error('No hay datos para las fechas seleccionadas')
    
    
    row1[0].metric("Temperature", "70 °F", "1.2 °F")
    row1[1].metric("Wind", "9 mph", "-8%")
    row1[2].metric("Humidity", "86%", "4%")
    row1[3].metric("Batería", "37%", "-2%")
    
    # Mostrar los datos en forma de tabla
    row2[0].subheader('Datos en forma de tabla:')
    df = pd.DataFrame(list(zip(lst, lst2)),
                      json_data['data']['index'],
                      columns =['valores_medios', 'pasos'])
    
    @st.cache_data
    def convert_df_to_csv(df):
      # IMPORTANT: Cache the conversion to prevent computation on every rerun
      return df.to_csv().encode('utf-8')
    
    row2[0].download_button(
      label = "Descargar datos como CSV",
      data = convert_df_to_csv(df),
      file_name = 'datos.csv',
      mime = 'text/csv',
    )
    
    row2[0].write(df)
    
    
    mention(
        label="GO ARISTEO",
        icon="🧀",  # Some icons are available... like Streamlit!
        url="https://quesandaluz.es/go-aristeo/",
    )
    
    row2[1].subheader('Gráfico:')
    columna_grafico = row2[1].selectbox('Seleccione la columna para el gráfico:', df.columns)
    fig = px.line(x=df.index, y=df[columna_grafico])
    row2[1].plotly_chart(fig)
