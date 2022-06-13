import streamlit as st
import requests
from shapely.geometry import Polygon
import pandas as pd
import geopandas as gpd
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
    def find_min(df, coor):
        x=((df['lat']-coor[0])**2+(df['lon']-coor[1])**2).argmin()
        return x
    col1, col2=st.columns(2)
    """
    Для начала посмотрим на статистику по районам города
    """
    with col1:
        city=st.selectbox('Выберите ваш город', ['Москва', 'Санкт-Петербург'])
    with col2:
        type_help=st.selectbox('Выберите интересующий вас вид помощи', list(data[2][0]['properties'].keys())[2:])
    if city=='Москва':
        dis=data[0]
        hos=data[2]
    else:
        dis=data[1]
        hos=data[3]
    districts=[]
    for i in dis:
        districts.append([i['id'], i['properties'][type_help], Polygon(i['geometry']['coordinates'][0])])
    districts=gpd.GeoDataFrame(pd.DataFrame(districts, columns=['name','count','geometry']),geometry='geometry')
    districts=districts[districts['count']>0]
    a=dict({'Москва':[55.75215, 37.61819], 'Санкт-Петербург':[59.9238, 30.3796 ]})
    m=folium.Map(a[city], zoom_start=12)
    districts.explore('count', m=m)
    folium_static(m)
    col1, col2=st.columns(2)
    """
    Теперь найдем ближайшую к вам больницу оказывающую такой типо помощи. Введите адресс из города который вы выбрали выше
    """
    with col1:
        street = st.text_input('Введите улицу')
    with col2:
        house_number = st.text_input('Введите номер дома')
    entrypoint='https://nominatim.openstreetmap.org/search?'
    coordinates=[]
    if len(house_number)>0:
        params={'city':city, 'street': house_number+', '+street, 'format': 'geojson'}
        r=requests.get(entrypoint,params)
        r.json()
        if len(r.json()['features']) >0:
            coordinates=r.json()['features'][0]['geometry']['coordinates']
        else:
            st.write('Попробуйте написать по другому')
    hospitals=[]
    if city=='Москва':
        keys1='name'
    else:
        keys1='index'
    for i in hos:
        hospitals.append([i['properties'][keys1],i['properties'][type_help],i['geometry']['coordinates'] ])
    hospitals=pd.DataFrame(hospitals)
    hospitals= hospitals[[0,1]].join(pd.DataFrame(hospitals[2].tolist(), columns=['lat','lon']))
    hospitals= hospitals[hospitals[1]==1]
    if len(hospitals)==0:
        st.write('В вашем городе нет таких МО')
    else:
        if len(coordinates)>0:
            x=find_min(hospitals,coordinates)
            a=hospitals.iloc[x]
            url='https://nominatim.openstreetmap.org/reverse?'
            params={'format':'json','lon': a['lat'], 'lat':a['lon']}
            r=requests.get(url,params)
            name_min=r.json()['display_name']
            st.write('Ближайшая больница предоставляющуя помощь вида '+type_help+' это '+a[0]+' находящаяся по адресу '+ name_min)
        else:
            st.write('Попробуйте по другому')
       
        
