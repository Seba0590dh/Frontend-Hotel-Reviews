import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit as st
import requests
import json

host = 'http://127.0.0.1:8000'

txt = st.text_area('Text to analyze')

st.write('Length:', len(txt))


if st.button('Consultar'):
    # print is visible in the server output, not in the page
    print('button clicked!')
    x = requests.get(host+'/search', params={'search_query':txt})
    data = json.loads(x.text)
else:
    st.write('I was not clicked 😞')
    data = {}

# Cargar el dataset desde el archivo CSV
#df = pd.read_csv('data/dataset20.csv')


df = pd.DataFrame.from_records(data =data)

if df.shape[0]:
    # Eliminar filas con valores NaN
    df_cleaned = df.dropna(subset=['lat', 'lng'])

    # Obtener las primeras 20 coordenadas únicas y los nombres de los hoteles
    coordenadas_unicas = df_cleaned[['lat', 'lng']].drop_duplicates().head(20).values.tolist()
    nombres_hoteles = df_cleaned['hotel_name'].drop_duplicates().head(20).values.tolist()

    # Crear un mapa centrado en el punto medio de las coordenadas
    latitudes = [coord[0] for coord in coordenadas_unicas]
    longitudes = [coord[1] for coord in coordenadas_unicas]
    center_lat = sum(latitudes) / len(latitudes)
    center_lng = sum(longitudes) / len(longitudes)

    # Crear un mapa con centro automático y ajuste de límites
    map = folium.Map(location=[center_lat, center_lng], width='100%', height='100%', fullscreen_control=True)

    # Crear un grupo de marcadores
    marker_cluster = MarkerCluster()

    # Agregar marcadores para cada coordenada única con el nombre del hotel y la información adicional en el cuadro emergente
    for coord, nombre_hotel in zip(coordenadas_unicas, nombres_hoteles):
        lat, lng = coord
        hotel_info = df_cleaned.loc[df_cleaned['hotel_name'] == nombre_hotel]
        hotel_address = hotel_info['hotel_address'].values[0]
        average_score = hotel_info['reviewer_score'].values[0] #Cambien average_score por reviewer_score
        tooltip = folium.Tooltip(nombre_hotel)
        popup_content = f"<b>{nombre_hotel}</b><br><b>Address:</b> {hotel_address}<br><b>Average Score:</b> {average_score}"
        popup = folium.Popup(popup_content, max_width=300)  # Ajustar el ancho máximo del cuadro emergente
        marker = folium.Marker([lat, lng], tooltip=tooltip, popup=popup)
        marker_cluster.add_child(marker)

    # Agregar el grupo de marcadores al mapa
    map.add_child(marker_cluster)

    # Ajustar los límites del mapa para que se muestren todos los marcadores con un margen adicional
    margin_factor = 0.1
    margin_lat = (max(latitudes) - min(latitudes)) * margin_factor
    margin_lng = (max(longitudes) - min(longitudes)) * margin_factor
    map.fit_bounds([[min(latitudes) - margin_lat, min(longitudes) - margin_lng], [max(latitudes) + margin_lat, max(longitudes) + margin_lng]])

    # Mostrar el mapa en Streamlit
    st.title('Mapa de Hoteles')
    st.write('Primeros 20 hoteles')

    folium_static(map)
