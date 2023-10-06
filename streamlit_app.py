# https://blog.streamlit.io/host-your-streamlit-app-for-free/

import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
import json


# Fiware STH: Quantum
quantum_server = 'atdfiware.grayhats.com'
quantum_endpoint = '/quantum/v2'

# Fiware Structure Service
fiwareservice = 'smarttrebol'
fiwareservicepath = '/rabanales'

#num_datos = 5

#print(json.dumps(response.json(), indent=4))


# Título de la aplicación
st.title('Aplicación para visualizar y descargar datos desde JSON')

num_options = ['1', '3', '5', '10', '20']
num_datos = st.selectbox('Seleccione el número de datos:', num_options)
                         
# Petición de servicio en base a la información global definida previamente.
accion = '/entities/urn:ngsi-ld:atdnoise:atd-noise-000/value?lastN='+str(num_datos)
url = 'https://'+quantum_server+quantum_endpoint+accion

payload={}
headers = {
  'Fiware-Service': fiwareservice,
  'Fiware-ServicePath': fiwareservicepath
}

response = requests.request("GET", url, headers=headers, data=payload)

json_data = response.json()

lst = json_data['data']['attributes'][1]['values']
lst2 = json_data['data']['attributes'][4]['values']


# Mostrar los datos en forma de tabla
st.subheader('Datos en forma de tabla:')
df = pd.DataFrame(list(zip(lst, lst2)),
                  json_data['data']['index'],
                  columns =['valores_medios', 'pasos'])
st.write(df)

@st.cache_data
def convert_df_to_csv(df):
  # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')

st.download_button(
  label = "Descargar datos como CSV",
  data = convert_df_to_csv(df),
  file_name = 'datos.csv',
  mime = 'text/csv',
)

# Mostrar los datos en forma de gráfico
st.subheader('Gráfico:')
columna_grafico = st.selectbox('Seleccione la columna para el gráfico:', df.columns)
fig, ax = plt.subplots()
ax.plot(df.index, df[columna_grafico], marker='o', linestyle='-')
plt.xlabel('Índice')
plt.ylabel(columna_grafico)
st.pyplot(fig)
