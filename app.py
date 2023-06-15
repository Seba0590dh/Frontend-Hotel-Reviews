import pandas as pd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit as st

# Cargar el dataset desde el archivo CSV
df = pd.read_csv('data/dataset20.csv')

# Eliminar filas con valores NaN
df_cleaned = df.dropna(subset=['lat', 'lng'])

# Obtener las primeras 20 coordenadas unicas y los nombres de los hoteles
coordenadas_unicas = df_cleaned[['lat', 'lng']].drop_duplicates().head(20).values.tolist()
nombres_hoteles = df_cleaned['Hotel_Name'].drop_duplicates().head(20).values.tolist()

# Crear un mapa centrado en el punto medio de las coordenadas
latitudes = [coord[0] for coord in coordenadas_unicas]
longitudes = [coord[1] for coord in coordenadas_unicas]
center_lat = sum(latitudes) / len(latitudes)
center_lng = sum(longitudes) / len(longitudes)

# Crear un mapa con centro automatico y ajuste de limites
map = folium.Map(location=[center_lat, center_lng], width='50%', height='50%')

# Crear un grupo de marcadores
marker_cluster = MarkerCluster()

# Agregar marcadores para cada coordenada unica con el nombre del hotel en el cuadro emergente
for coord, nombre_hotel in zip(coordenadas_unicas, nombres_hoteles):
    lat, lng = coord
    tooltip = folium.Tooltip(nombre_hotel)
    marker = folium.Marker([lat, lng], tooltip=tooltip)
    marker_cluster.add_child(marker)

# Agregar el grupo de marcadores al mapa
map.add_child(marker_cluster)

# Ajustar los limites del mapa para que se muestren todos los marcadores con un margen adicional
margin_factor = 0.1
margin_lat = (max(latitudes) - min(latitudes)) * margin_factor
margin_lng = (max(longitudes) - min(longitudes)) * margin_factor
map.fit_bounds([[min(latitudes) - margin_lat, min(longitudes) - margin_lng], [max(latitudes) + margin_lat, max(longitudes) + margin_lng]])

# Mostrar el mapa en Streamlit
st.title('Mapa de Hoteles')
st.write('Primeros 10 hoteles')

folium_static(map)



