import pandas as pd
# import numpy as np
import requests 
# import matplotlib.pyplot as plt
import geopandas as gpd
# import json
from shapely.geometry import Point
import folium
# from folium.plugins import TimestampedGeoJson
import streamlit as st
# import webbrowser
from streamlit_folium import st_folium


st.set_page_config()
st.title('EVs and their charge points in Amsterdam')


#%%
@st.cache_data
def laadpaal_data():
    return pd.read_csv('laadpaaldata.csv')
    
# laadpaal_data.describe()

@st.cache_data
def map_request():
    return requests.get('https://maps.amsterdam.nl/open_geodata/geojson_lnglat.php?KAARTLAAG=INDELING_STADSDEEL&THEMA=gebiedsindeling')

@st.cache_data
def df_creation():
    response = requests.get("https://api.openchargemap.io/v3/poi/?output=json&countrycode=NL&latitude=52.378&longitude=4.9&distance=25&distanceunit=km&maxresults=1000&compact=true&verbose=false&key=2ef595ab-9648-4d99-893b-f70fa0c47eeb")

    ###Dataframe bevat kolom die een list zijn. 
    #Met json_normalize zet je de eerste kolom om naar losse kolommen
    Laadpalen = pd.json_normalize(response.json())
    #Daarna nog handmatig kijken welke kolommen over zijn in dit geval Connections
    #Kijken naar eerst laadpaal op de locatie
    #Kan je uitpakken middels:
    df4 = pd.json_normalize(Laadpalen.Connections)
    df5 = pd.json_normalize(df4[0])
    # df5.head()
    ###Bestanden samenvoegen
    Laadpalen = pd.concat([Laadpalen, df5], axis=1)

    Laadpalen['geometry'] = Laadpalen.apply(lambda x: Point((x['AddressInfo.Longitude'], x['AddressInfo.Latitude'])),axis = 1)
    Laadpalen_geo = gpd.GeoDataFrame(Laadpalen, crs='EPSG:4326')
    mapp = map_request()
    return gpd.sjoin(mapp, Laadpalen_geo, predicate='contains')

AMS_laadpalen = df_creation().reset_index(drop=True)



def display_time_filters(df):
    year_list = list(df['DateCreated'].dt.year.unique())
    year_list.sort()
    year = st.sidebar.selectbox('Year', year_list, len(year_list)-1)
    # quarter = st.sidebar.radio('Quarter', [1, 2, 3, 4])
    # st.header(f'{year} Q{quarter}')
    return year#, quarter


def display_state_filter(df, district_name):
    district_list = [''] + list(df['Stadsdeel'].unique())
    district_list.sort()
    district_index = district_list.index(district_name) if district_name and district_name in district_list else 0
    return st.sidebar.selectbox('District', district_list, district_index)


def display_map_type():
    return st.sidebar.radio('Which data you want', ['Charge points', 
                                                    'Cars',
                                                    'Charging Behaviour'])


def CP_facts(df):#, year, district=None):
    # charger_level_list = list(df['LevelID'].unique())
    # charger_level = st.selectbox('Charger Level', list(df['LevelID'].unique()))
    # charger_level_count = df.loc[df['LevelID'] == charger_level].count()
    
    districts = df['Stadsdeel'].sort_values().unique()
    val = [None]* len(districts)
    with st.expander('Districts'):
        for i, dist in enumerate(districts):
            # create a checkbox for each category
            val[i] = st.checkbox(dist, value=True) # value is the preselect value for first render

    # filter data based on selection
    df_flt = df[df.Stadsdeel.isin(districts[val])].reset_index(drop=True)
    
    df_flt_crosstab = pd.crosstab(df_flt.Stadsdeel, df_flt.LevelID, margins=True)
    st.write(df_flt_crosstab)
    
    # col1, col2, col3 = st.columns(3)
    
    # with col1:
    #     for i, dist in enumerate(districts):
    #         # create a checkbox for each category   
    #         if dist:
    #             st.metric(f'Level 1 Chargers in {dist}', df_flt.loc[(df_flt['LevelID'] == 1) & (df['Stadsdeel'] == dist)]['LevelID'].count())    
    
    # with col2:
    #     st.metric('Level 2 Chargers', df_flt.loc[df_flt['LevelID'] == 2]['LevelID'].count())
    # with col3:
    #     st.metric('Level 3 Chargers', df_flt.loc[df_flt['LevelID'] == 3]['LevelID'].count())
    
    # if district:
    #     chargers = df.groupby('Stadsdeel')['UUID'].count().sort_values(ascending=False)
    
    
CP_facts(AMS_laadpalen)


#%%
    
# leg_kwds={'title':'Stadsdeel', 'loc': 'upper left', 'bbox_to_anchor':(1, 1.03), 'ncol':1}

# mapp.plot(column='Stadsdeel',cmap='Set3',legend=True,legend_kwds=leg_kwds)
# plt.title('Amsterdam')
# plt.show()

#%%

# AMS_laadpalen['PowerKW'].value_counts()

# AMS_laadpalen['LevelID'].value_counts()


# - Level 1: P < 3.7 kW
# - Level 2: 3.7 <= kW < P <= 37 kW
# - Level 3: 37 kw < P 
# 

#%%

ams_center = AMS_laadpalen.geometry.centroid[0]
# amsterdam_map = folium.Map(location = [ams_center.y, ams_center.x])

# geom = AMS_laadpalen.drop_duplicates('Stadsdeel').reset_index()

# # add the outline of district one
# folium.GeoJson(geom.geometry).add_to(amsterdam_map)

# for row in AMS_laadpalen.iterrows():    
#     row_values = row[1] 
#     folium.Marker(location = [row_values['AddressInfo.Latitude'], row_values['AddressInfo.Longitude']],
#                   popup = str(row_values["AddressInfo.ID"]),
#                   icon=folium.Icon(color='blue',
#                         icon_color='white',
#                         icon='charging-station',
#                         prefix='fa')).add_to(amsterdam_map)


# # amsterdam_map.save("amsterdam_map2.html")
# # webbrowser.open("amsterdam_map2.html")

# st_map = st_folium(amsterdam_map, width=1500, height=450)

#%%

# TimestampedGeoJson(AMS_laadpalen, transition_time=20).add_to(amsterdam_map)


# 1. Animated map showing CP installation per year:
#     - in blue: installed CPs
#     - in green: newly installed CPs
# 
# 2. Drop down to select charging power/stantard/CP type
# 3. For each selection display a count of CPs per district
# 


#%%


features2 = [
    {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row['AddressInfo.Longitude'], row['AddressInfo.Latitude']],
        },
        "properties": {
            "time": row["DateCreated"],
            "popup": row["AddressInfo.ID"],
#             "icon": folium.Icon(color='blue',
#                        icon_color='white',
#                        icon='charging-station',
#                        prefix='fa')
        },
    }
    for point,row in AMS_laadpalen.iterrows()
]


#%%


m = folium.Map(
    location=[ams_center.y, ams_center.x],
    tiles="Cartodb Positron",
    zoom_start=12,
)

folium.plugins.TimestampedGeoJson(
    {"type": "FeatureCollection", "features": features2},
    period="P1M",
    add_last_point=True,
    auto_play=False,
    loop=False,
    max_speed=0.5,
    loop_button=True,
#     date_options="YYYY/MM/DD",
    date_options="DD/MM/YYYY",
    time_slider_drag_update=True,
).add_to(m)

st_map = st_folium(m, width=1500, height=450)

# m.save("amsterdam_map.html")
# webbrowser.open("amsterdam_map.html")

#%%





# In[252]:

@st.cache_data
def cars_func():
    cars = requests.get('https://opendata.rdw.nl/resource/8jni-y848.json?$limit=50000&$offset=0')#&$order=ID')
    cars2 = requests.get('https://opendata.rdw.nl/resource/8jni-y848.json?$limit=50000&$offset=50000')#&$order=ID')
    cars3 = requests.get('https://opendata.rdw.nl/resource/8jni-y848.json?$limit=50000&$offset=100000')#&$order=ID')
    cars4 = requests.get('https://opendata.rdw.nl/resource/8jni-y848.json?$limit=50000&$offset=150000')#&$order=ID')
    
    cars = pd.DataFrame(cars.json())
    cars2 = pd.DataFrame(cars2.json())
    cars3 = pd.DataFrame(cars3.json())
    cars4 = pd.DataFrame(cars4.json())
    
    cars = pd.DataFrame(cars)
    cars = pd.concat([cars,cars2],ignore_index=True)
    cars = pd.concat([cars,cars3],ignore_index=True)
    cars = pd.concat([cars,cars4],ignore_index=True)
    
    cars = cars.assign(datum_tenaamstelling = pd.to_datetime(cars.datum_tenaamstelling, format = '%Y%m%d'))
    cars = cars.assign(vervaldatum_apk = pd.to_datetime(cars.vervaldatum_apk, format = '%Y%m%d'))
    cars = cars.assign(datum_eerste_tenaamstelling_in_nederland = pd.to_datetime(cars.datum_eerste_tenaamstelling_in_nederland, format = '%Y%m%d'))

    cars = cars[['kenteken', 'voertuigsoort', 'merk', 'handelsbenaming',
           'vervaldatum_apk', 'datum_tenaamstelling',  'datum_eerste_tenaamstelling_in_nederland',
           'inrichting', 'aantal_zitplaatsen', 'eerste_kleur', 'maximale_constructiesnelheid',
           'aantal_deuren', 'aantal_wielen', 'lengte', 'breedte', 'europese_voertuigcategorie',
           'taxi_indicator']]
    
    return cars

# cars = cars_func()

# taxis = cars.loc[cars.taxi_indicator == 'Ja'].reset_index()
# taxis.value_counts(['merk','handelsbenaming'])


#%%

# cars.value_counts('merk')
# cars.value_counts('inrichting')
# cars.value_counts('kleur')

# cars.groupby(cars.datum_tenaamstelling.dt.year)['kenteken'].count().plot(kind='bar')

# cars.groupby(cars.datum_tenaamstelling.dt.month)['kenteken'].count().plot(kind='bar')

#%%

