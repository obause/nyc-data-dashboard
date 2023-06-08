import pandas as pd
import json
import geopandas as gpd
from shapely.geometry import shape
from shapely import wkt

import plotly.express as px
#import chart_studio.plotly as py
import plotly.graph_objects as go
#from plotly.offline import init_notebook_mode, iplot, plot

class Data:
    def __init__(self, filepath, format, description=None):
        self.filepath = filepath
        if format == 'csv':
            self.df = pd.read_csv(filepath)
        elif format == 'json':
            self.df = pd.read_json(filepath)
        self.data_description = description
    
    def preprocess(self):
        pass
    
def get_borough_mappings():
    borough_mapping = pd.DataFrame({
        "borough_name": ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
        "boro_code": [1, 2, 3, 4, 5],
        "boro_short1": ["M", "X", "B", "Q", "R"],
        "boro_short2": ["M", "B", "K", "Q", "S"],
        "Latitude": [40.776676,40.837048,40.650002,40.742054,40.579021],
        "Longitude": [-73.971321,-73.865433,-73.949997,-73.769417, -74.151535]
    })
    return borough_mapping


def get_crime_arrests(truncated=True):
    if truncated:
        nypd_arrests = pd.read_csv('data/crime/arrests_2022.csv')
    else:
        nypd_arrests = pd.read_csv('data/crime/arrests_2022.csv')
    date = nypd_arrests['ARREST_DATE'].str.split("/", n = 3, expand = True)
    nypd_arrests['year'] = date[2].astype('int32')
    nypd_arrests['day'] = date[1].astype('int32')
    nypd_arrests['month'] = date[0].astype('int32')
    return nypd_arrests
    
def get_crime_shootings(year=2022):
    nypd_shootings = pd.read_csv('data/crime/NYPD_Shooting_Incident_Data__Historic_.csv')
    nypd_shootings['OCCUR_DATE'] = pd.to_datetime(nypd_shootings['OCCUR_DATE'])
    nypd_shootings['YEAR'] = pd.DatetimeIndex(nypd_shootings['OCCUR_DATE']).year
    nypd_shootings = nypd_shootings[nypd_shootings['YEAR'] == year]
    return nypd_shootings

def get_nyc_borough_indicators():
    boro_indicators = pd.read_csv('data/social/boro_cd_attributes.csv')
    nyc_indicators = pd.read_csv('data/social/city_cd_attributes.csv')
    nyc_indicators['borough'] = 'New York City'
    indicators = pd.concat([boro_indicators, nyc_indicators]).reset_index(drop=True)
    indicators_legend = {
        'under18_rate': 'Age under 18', 
        'over65_rate': 'Age 65 & Over',
        'lep_rate': 'Limited English Proficiency', 
        'pct_hh_rent_burd': 'Rent Burdened',
        'poverty_rate': 'Poverty Rate',
        'unemployment': 'Unemployment Rate',
        'crime_per_1000': 'Crime Rate',
        }
    indicators.rename(columns=indicators_legend, inplace=True)
    return indicators

def get_hospital_data():
    hospitals = pd.read_csv('data/social/NYC_Health___Hospitals_patient_care_locations_-_2011.csv')
    return hospitals

def get_car_accident_data():
    car_accidents = pd.read_csv('data/crime/car_accidents_2022.csv')
    return car_accidents

def get_air_quality_data(measure_name='Fine Particulate Matter (PM2.5)', time_period='Annual Average 2020'):
    air_quality = pd.read_csv("data/social/NYCgov_Air_Quality.csv")
    air_quality = air_quality[air_quality['Name'] == measure_name]
    nyc_cd = pd.read_csv("data/reference_data/nycd.csv")
    pd_by_cm = air_quality[(air_quality['Geo Type Name'] == 'UHF42') & (air_quality['Time Period'] == time_period)]
    #pd_by_cm = pd.merge(air_quality, nyc_cd, left_on='Geo Join ID', right_on='BoroCD')
    pd_by_cm['Name'].unique()
    nyc_cd['geometry'] = nyc_cd['the_geom'].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(nyc_cd, crs='epsg:4326')
    gdf.drop('the_geom', axis=1, inplace=True)
    multipolygon_json = json.loads(gdf.to_json())
    gdf = gdf.set_index('BoroCD')
    
    return multipolygon_json, pd_by_cm
    

def get_squirrels():
    squirrels = pd.read_csv('data/environment/2018_Central_Park_Squirrel_Census_-_Squirrel_Data.csv')
    return squirrels

def get_nypd_precincts_geodata():
    with open('data/crime/Police_Precincts.geojson') as f:
        nypd_precincts_geo = json.load(f)
    return nypd_precincts_geo

def get_park_geodata():
    with open('data/Parks_Properties.geojson') as f:
        nyc_parks_geo = json.load(f)
    return nyc_parks_geo

def get_community_districts_geodata():
    with open("data/reference_data/UHF42.geo.json") as f:
        nyc_uhf42_geo = json.load(f)
    return nyc_uhf42_geo

def get_borough_geodata():
    with open("data/Borough_Boundaries.geojson") as f:
        nyc_borough_geo = json.load(f)
    return nyc_borough_geo