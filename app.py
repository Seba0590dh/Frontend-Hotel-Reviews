import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit as st
import requests
import json
import pandas as pd

st.set_page_config(layout='wide')

st.markdown("""
        <style>
               * {
                    padding-left: 0rem;
                    padding-right: 0rem;
                    margin-left: 0rem;
                    margin-right: 0rem;
                }
        </style>
        """, unsafe_allow_html=True)

host = 'https://hotel-reviews-api-vp2e4dlnjq-uc.a.run.app'

# Dividir la interfaz en dos columnas
col1, col2 = st.columns(2)

# Contenido de la primera columna
with col1:
    # Mover el st.text_input a la esquina inferior izquierda
    txt = st.text_input('What hotel would you like?', key='input_col1')  # Cambiamos la clave 'input' por 'input_col1'
    st.write('Length:', len(txt))
    country = st.text_input('What country would you like?')

    x = requests.get(host+'/search', params={'search_query': txt,'country': country})
    data = json.loads(x.text)

    df = pd.DataFrame.from_records(data=data)

    if df.shape[0]:
        # Eliminar filas con valores NaN
        df_cleaned = df.dropna(subset=['lat', 'lng'])

        # Mostrar la tabla con la información del hotel
        selected_hotel = df_cleaned[df_cleaned['hotel_name'] == txt].head(1)
        if not selected_hotel.empty:
            st.write('Tabla de Hoteles')
            st.table(selected_hotel[['hotel_name', 'reviewer_score', 'hotel_address']])

        # Mostrar la tabla con los datos del dataframe
        st.write('Tabla de Hoteles')
        st.table(df[['hotel_name', 'reviewer_score', 'hotel_address','summary']])


# Contenido de la segunda columna
with col2:
    x = requests.get(host+'/search', params={'search_query': txt,'country':country})
    data = json.loads(x.text)

    df = pd.DataFrame.from_records(data=data)

    if df.shape[0]:
        # Eliminar filas con valores NaN
        df_cleaned = df.dropna(subset=['lat', 'lng'])

        # Obtener las primeras 20 coordenadas únicas y los nombres de los hoteles
        coordenadas_unicas = df_cleaned[['lat', 'lng']].values.tolist()
        nombres_hoteles = df_cleaned['hotel_name'].values.tolist()

        # Crear un mapa centrado en el punto medio de las coordenadas
        latitudes = [coord[0] for coord in coordenadas_unicas]
        longitudes = [coord[1] for coord in coordenadas_unicas]
        center_lat = sum(latitudes) / len(latitudes)
        center_lng = sum(longitudes) / len(longitudes)

        # Crear un mapa con centro automático y ajuste de límites
        map = folium.Map(location=[center_lat, center_lng], width='90%', height='100%', fullscreen_control=True)

        # Crear un grupo de marcadores
        marker_cluster = MarkerCluster()

        # Agregar marcadores para cada coordenada única con el nombre del hotel y la información adicional en el cuadro emergente
        for coord, nombre_hotel in zip(coordenadas_unicas, nombres_hoteles):
            lat, lng = coord
            hotel_info = df_cleaned.loc[df_cleaned['hotel_name'] == nombre_hotel]
            hotel_address = hotel_info['hotel_address'].values[0]
            reviewer_score = hotel_info['reviewer_score'].values[0]
            tooltip = folium.Tooltip(nombre_hotel)
            popup_content = f"<b>{nombre_hotel}</b><br><b>Address:</b> {hotel_address}<br><b>Reviewer Score:</b> {reviewer_score}"
            popup = folium.Popup(popup_content, max_width=300)
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
