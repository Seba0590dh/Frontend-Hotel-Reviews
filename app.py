import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
import streamlit as st
import requests
import json
import pandas as pd
from PIL import Image


st.set_page_config(layout='wide')

#col_img1, col_img2 = st.columns([2, 1])


image = Image.open('Img/Image20230622095242.jpg')

st.image(image, use_column_width= True)

#with col_img2:
    #image2 = Image.open('Img/hotel room with beachfront view.jpg')

    #st.image(image2, width=500,use_column_width=True)

# Add a text block with a welcome message and a brief summary
st.markdown('<h1 style="text-align: center;">Welcome to HotelQuest!</h1>', unsafe_allow_html=True)
st.markdown('<p class="bigger-text">Can\'t decide where to stay? No worries! We will help you find that ideal place. Just type for preferences and we\'ll do the rest.</p>', unsafe_allow_html=True)


# Load and display the additional image
#image2 = Image.open('Img/hotel_image.jpg')
#st.image(image2, use_column_width=True)

st.markdown(
    """
    <style>
        * {
            padding-left: 0rem;
            padding-right: 0rem;
            margin-left: 0rem;
            margin-right: 0rem;
        }
        .bigger-text {
            font-size: 24px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

host = 'https://hotel-reviews-vp2e4dlnjq-uc.a.run.app'

# Input txt
txt = st.text_input('What would you like in your ideal hotel?', key='input_col1')  # Cambiamos la clave 'input' por 'input_col1'


country_options = ['United Kingdom', 'Netherlands', 'Spain', 'France', 'Austria', 'Italy']
country = st.selectbox('Select a country', country_options)


def request_function():
    x = requests.get(host+'/search', params={'search_query': txt, 'country': country})
    data = json.loads(x.text)

    df = pd.DataFrame.from_records(data=data)
    return df


df = pd.DataFrame()

if st.button("Search"):
    df = st.session_state["data"] = request_function()


if 'data' in st.session_state:
    df = st.session_state['data']

if df.shape[0]:
    # Eliminar filas con valores NaN
    df_cleaned = df.dropna(subset=['lat', 'lng'])

    if df_cleaned.shape[0]:
        # Create a column layout
        col_map, col_table = st.columns([2, 1])

        # Display the map in the left column
        with col_map:
            # coordenadas
            coordenadas_unicas = df_cleaned[['lat', 'lng']].values.tolist()
            nombres_hoteles = df_cleaned['hotel_name'].values.tolist()

            # Map centrado en el midpoint de las coordinates
            latitudes = [coord[0] for coord in coordenadas_unicas]
            longitudes = [coord[1] for coord in coordenadas_unicas]
            center_lat = sum(latitudes) / len(latitudes)
            center_lng = sum(longitudes) / len(longitudes)
            map = folium.Map(location=[center_lat, center_lng], width='90%', height='100%', fullscreen_control=True)

            # Create a marker cluster for the hotels
            marker_cluster = MarkerCluster()

            # Markers para cada hotel con popup information
            for coord, nombre_hotel in zip(coordenadas_unicas, nombres_hoteles):
                lat, lng = coord
                hotel_info = df_cleaned.loc[df_cleaned['hotel_name'] == nombre_hotel]
                hotel_address = hotel_info['hotel_address'].values[0]
                #summary = hotel_info['summary'].values[0]
                reviewer_score = hotel_info['reviewer_score'].values[0]
                tooltip = folium.Tooltip(nombre_hotel)
                popup_content = f"<b>{nombre_hotel}</b><br><b>Address:</b> {hotel_address}</b><br><b>Reviewer Score:</b> {reviewer_score}"
                popup = folium.Popup(popup_content, max_width=300)
                marker = folium.Marker([lat, lng], tooltip=tooltip, popup=popup)

                # Add the marker to the marker cluster
                marker_cluster.add_child(marker)

            # Add the marker cluster to the map
            map.add_child(marker_cluster)

            # Fit the map bounds to display all markers with additional margin
            margin_factor = 0.1
            margin_lat = (max(latitudes) - min(latitudes)) * margin_factor
            margin_lng = (max(longitudes) - min(longitudes)) * margin_factor
            map.fit_bounds([[min(latitudes) - margin_lat, min(longitudes) - margin_lng],
                            [max(latitudes) + margin_lat, max(longitudes) + margin_lng]])

            # Show the map in Streamlit
            st.title('Hotel recommendations')
            st.markdown('<p class="bigger-text">Here are 20 recommendations for hotels that suit your needs. Check them out!</p>',unsafe_allow_html=True)
            folium_static(map)

            # Get the selected hotel from the dropdown menu
            st.title('Select your hotel')
            st.markdown('<p class="bigger-text">Select a hotel to see its exact location and check what people have written about it!</p>', unsafe_allow_html=True)
            selected_hotel = st.selectbox("", nombres_hoteles, key='dropdown',)

            if selected_hotel:
                selected_row = df_cleaned[df_cleaned['hotel_name'] == selected_hotel].index[0]
                selected_summary = df_cleaned.loc[selected_row, 'summary']

                # Clear the map and add only the selected hotel's marker
                map = folium.Map(location=[center_lat, center_lng], width='90%', height='100%', fullscreen_control=True)
                marker = folium.Marker(
                    [df_cleaned.loc[selected_row, 'lat'], df_cleaned.loc[selected_row, 'lng']],
                    tooltip=selected_hotel,
                    popup=folium.Popup(
                        f"<b>{selected_hotel}</b><br><b>Address:</b> {df_cleaned.loc[selected_row, 'hotel_address']}<br><b>Reviewer Score:</b> {df_cleaned.loc[selected_row, 'reviewer_score']}",
                        max_width=300,
                    ),
                )
                map.add_child(marker)

                folium_static(map)

                # Show the selected hotel's summary
                st.write("Selected Summary:")
                st.write(selected_summary)

        # Display the table in the right column
        with col_table:
           # Display the initial table with hotel_name and reviewer_score
            df_cleaned['reviewer_score'] = df_cleaned['reviewer_score'].apply(lambda x: '{:.1f} ⭐'.format(x))
            st.write('Hotel Names and Review Scores')
            table = st.table(df_cleaned[['hotel_name', 'reviewer_score']])
