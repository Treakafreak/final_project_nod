import streamlit as st
import requests
from shapely.geometry import Polygon
import pandas as pd
import geopandas as gpd
import plotly.express as px
from streamlit_folium import folium_static
import folium
with st.echo(code_location='below'):
    @st.cache
    def get_data():
        data_urls=[
            'https://raw.githubusercontent.com/Treakafreak/final_project_nod/main/districts_msk.json',
            'https://raw.githubusercontent.com/Treakafreak/final_project_nod/main/districts_spb.json',
            'https://raw.githubusercontent.com/Treakafreak/final_project_nod/main/moscow_df_final.json',
            'https://raw.githubusercontent.com/Treakafreak/final_project_nod/main/spb_df_final.json'
        ]
        x=[]
        for i in data_urls:
            x.append(requests.get(i).json()['features'])
        return x
    data=get_data()
    col1, col2=st.columns(2)
    with col1:
        city=st.selectbox('Выберите ваш город', ['Москва', 'Санкт-Петербург'])
    with col2:
        type_help=st.selectbox('Выберите интересующий вас вид помощи', list(data[2][0]['properties'].keys())[2:])
    if city=='Москва':
        dis=data[0]
        hos=data[2]
    districts=[]
    for i in dis:
        districts.append([i['id'], i['properties'][type_help], Polygon(i['geometry']['coordinates'][0])])
    districts=gpd.GeoDataFrame(pd.DataFrame(districts, columns=['name','count','geometry']),geometry='geometry')
    a=dict({'Москва':[55.75215, 37.61819], 'Санкт-Петербург':[59.9238, 30.3796 ]})
    m=folium.Map(a[city], zoom_start=12)
    districts.explore('count',m=m)
    folium_static(m)