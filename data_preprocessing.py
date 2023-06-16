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

def calculate_centroids(gdf, geometry_column='geometry'):
    gdf = gdf.to_crs('epsg:4326')
    gdf['Longitude'] = gdf[geometry_column].to_crs('epsg:4326').centroid.x
    gdf['Latitude'] = gdf[geometry_column].to_crs('epsg:4326').centroid.y

def get_crime_arrests(truncated=True):
    if truncated:
        nypd_arrests = pd.read_csv('data/crime/arrests_2022.csv')
    else:
        nypd_arrests = pd.read_csv('data/crime/arrests_2022.csv')
    date = nypd_arrests['ARREST_DATE'].str.split("/", n = 3, expand = True)
    nypd_arrests['year'] = date[2].astype('int32')
    nypd_arrests['day'] = date[1].astype('int32')
    nypd_arrests['month'] = date[0].astype('int32')
    nypd_arrests['ARREST_DATE'] = f"{nypd_arrests['day']}.{nypd_arrests['month']}.{nypd_arrests['year']}"
    return nypd_arrests
    
def get_crime_shootings(year=2022):
    nypd_shootings = pd.read_csv('data/crime/NYPD_Shooting_Incident_Data__Historic_.csv')
    nypd_shootings['OCCUR_DATE'] = pd.to_datetime(nypd_shootings['OCCUR_DATE'])
    nypd_shootings['YEAR'] = pd.DatetimeIndex(nypd_shootings['OCCUR_DATE']).year
    nypd_shootings = nypd_shootings[nypd_shootings['YEAR'] == year]
    nypd_shootings['OCCUR_DATE'] = nypd_shootings['OCCUR_DATE'].dt.strftime('%d.%m.%Y')
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

def get_cd_indicators():
    cd_indicators = pd.read_csv('data/social/cd_demographic_race_economics.csv')
    return cd_indicators

def get_hospital_data():
    hospitals = pd.read_csv('data/social/NYC_Health___Hospitals_patient_care_locations_-_2011.csv')
    return hospitals

def get_car_accident_data():
    car_accidents = pd.read_csv('data/crime/car_accidents_2022.csv')
    return car_accidents

def get_air_quality_data(measure_name='All', time_period='All'):
    air_quality = pd.read_csv("data/social/NYCgov_Air_Quality.csv")
    if measure_name != 'All':   
        air_quality = air_quality[air_quality['Name'] == measure_name]
    #nyc_cd = pd.read_csv("data/reference_data/nycd.csv")
    if time_period != 'All':
        air_quality = air_quality[(air_quality['Geo Type Name'] == 'UHF42') & (air_quality['Time Period'] == time_period)]
    else:
        air_quality = air_quality[(air_quality['Geo Type Name'] == 'UHF42')]
    #pd_by_cm = pd.merge(air_quality, nyc_cd, left_on='Geo Join ID', right_on='BoroCD')
    #nyc_cd['geometry'] = nyc_cd['the_geom'].apply(wkt.loads)
    #gdf = gpd.GeoDataFrame(nyc_cd, crs='epsg:4326')
    #gdf.drop('the_geom', axis=1, inplace=True)
    #multipolygon_json = json.loads(gdf.to_json())
    #gdf = gdf.set_index('BoroCD')
    
    return air_quality
    
def get_cd_demographic_data():
    demo_ages = pd.read_csv("data/social/cd_demographic_age_gender.csv")

    #demo_ages_test = demo_ages[demo_ages['cd_number'] == 201]
    #demo_ages_female = demo_ages_test.iloc[:, 7:25]
    #demo_ages_male = demo_ages_test.iloc[:, 25:]
    demo_ages = demo_ages.iloc[:, 1:-4]
    demo_ages = demo_ages.drop(columns=demo_ages.iloc[:, 1:6])
    demo_ages_pivot = demo_ages.melt(id_vars=['cd_number'], var_name='age_group', value_name='value')
    demo_ages_pivot['gender'] = demo_ages_pivot['age_group'].str.split('_').str[2]
    legend = {
        'pop_pct_female_under_5': 'under 5', 
        'pop_pct_female_5_9': '5 to 9',
        'pop_pct_female_10_14': '10 to 14', 
        'pop_pct_female_15_19': '15 to 19',
        'pop_pct_female_20_24': '20 to 24',
        'pop_pct_female_25_29': '25 to 29',
        'pop_pct_female_30_34': '30 to 34',
        'pop_pct_female_35_39': '35 to 39',
        'pop_pct_female_40_44': '40 to 44',
        'pop_pct_female_45_49': '45 to 49',
        'pop_pct_female_50_54': '50 to 54',
        'pop_pct_female_55_59': '55 to 59',
        'pop_pct_female_60_64': '60 to 64',
        'pop_pct_female_65_69': '65 to 69',
        'pop_pct_female_70_74': '70 to 74',
        'pop_pct_female_75_79': '75 to 79',
        'pop_pct_female_80_84': '80 to 84',
        'pop_pct_female_85_over': '85 & over',
        'pop_pct_male_under_5': 'under 5',
        'pop_pct_male_5_9': '5 to 9',
        'pop_pct_male_10_14': '10 to 14',
        'pop_pct_male_15_19': '15 to 19',
        'pop_pct_male_20_24': '20 to 24',
        'pop_pct_male_25_29': '25 to 29',
        'pop_pct_male_30_34': '30 to 34',
        'pop_pct_male_35_39': '35 to 39',
        'pop_pct_male_40_44': '40 to 44',
        'pop_pct_male_45_49': '45 to 49',
        'pop_pct_male_50_54': '50 to 54',
        'pop_pct_male_55_59': '55 to 59',
        'pop_pct_male_60_64': '60 to 64',
        'pop_pct_male_65_69': '65 to 69',
        'pop_pct_male_70_74': '70 to 74',
        'pop_pct_male_75_79': '75 to 79',
        'pop_pct_male_80_84': '80 to 84',
        'pop_pct_male_85_over': '85 & over'
        }
    demo_ages_pivot.replace({'age_group': legend}, inplace=True)
    return demo_ages_pivot

def get_cd_demographic_legend():
    legend = {
        'pop_pct_female_under_5': 'under 5', 
        'pop_pct_female_5_9': '5 to 9',
        'pop_pct_female_10_14': '10 to 14', 
        'pop_pct_female_15_19': '15 to 19',
        'pop_pct_female_20_24': '20 to 24',
        'pop_pct_female_25_29': '25 to 29',
        'pop_pct_female_30_34': '30 to 34',
        'pop_pct_female_35_39': '35 to 39',
        'pop_pct_female_40_44': '40 to 44',
        'pop_pct_female_45_49': '45 to 49',
        'pop_pct_female_50_54': '50 to 54',
        'pop_pct_female_55_59': '55 to 59',
        'pop_pct_female_60_64': '60 to 64',
        'pop_pct_female_65_69': '65 to 69',
        'pop_pct_female_70_74': '70 to 74',
        'pop_pct_female_75_79': '75 to 79',
        'pop_pct_female_80_84': '80 to 84',
        'pop_pct_female_85_over': '85 & over',
        'pop_pct_male_under_5': 'under 5',
        'pop_pct_male_5_9': '5 to 9',
        'pop_pct_male_10_14': '10 to 14',
        'pop_pct_male_15_19': '15 to 19',
        'pop_pct_male_20_24': '20 to 24',
        'pop_pct_male_25_29': '25 to 29',
        'pop_pct_male_30_34': '30 to 34',
        'pop_pct_male_35_39': '35 to 39',
        'pop_pct_male_40_44': '40 to 44',
        'pop_pct_male_45_49': '45 to 49',
        'pop_pct_male_50_54': '50 to 54',
        'pop_pct_male_55_59': '55 to 59',
        'pop_pct_male_60_64': '60 to 64',
        'pop_pct_male_65_69': '65 to 69',
        'pop_pct_male_70_74': '70 to 74',
        'pop_pct_male_75_79': '75 to 79',
        'pop_pct_male_80_84': '80 to 84',
        'pop_pct_male_85_over': '85 & over'
        }
    return legend

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

def get_community_districts_geodf():
    #nyc_cd = pd.read_csv("../data/reference_data/nycd.csv")
    #nyc_cd['geometry'] = nyc_cd['the_geom'].apply(wkt.loads)
    #gdf = gpd.GeoDataFrame(nyc_cd, crs='epsg:4326')
    #gdf.drop('the_geom', axis=1, inplace=True)
    gdf = gpd.read_file('data/reference_data/UHF42.geo.json')
    #gdf = gdf.set_index('BoroCD')
    gdf = gdf.to_crs('epsg:4326')
    gdf['Longitude'] = gdf['geometry'].to_crs('epsg:4087').centroid.x
    gdf['Latitude'] = gdf['geometry'].to_crs('epsg:4087').centroid.y
    gdf['displayname'] = [f'{a} <br> {b}' for a, b in zip(gdf["GEOCODE"], gdf["GEONAME"])]
    return gdf

def get_borough_geodata():
    with open("data/Borough_Boundaries.geojson") as f:
        nyc_borough_geo = json.load(f)
    return nyc_borough_geo

def get_measures_radar():
    df_measures_2022 = pd.read_excel(
       io='data/measures_2022.xlsx',
       sheet_name ='CHP_all_data'
    )
    df_measures_2018 = pd.read_excel(
       io='data/measures_2018.xlsx',
       sheet_name ='CHP_all_data'
    )
    df_measures_2015 = pd.read_excel(
       io='data/measures_2015.xlsx',
       sheet_name ='CHP_all_data'
    )

    df_radar_2022 = df_measures_2022
    df_radar_2018 = df_measures_2018
    df_radar_2015 = df_measures_2015

    df_radar_2022 = df_radar_2022[["Borough","Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"]]
    df_radar_2022 = pd.melt(df_radar_2022, id_vars=["Borough"], var_name="Category", value_name="Percent", 
                                value_vars=["Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"])
    df_radar_2022 = df_radar_2022.round(decimals=0)

    df_radar_2018 = df_radar_2018[["Borough","Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"]]
    df_radar_2018 = pd.melt(df_radar_2018, id_vars=["Borough"], var_name="Category", value_name="Percent", 
                                value_vars=["Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"])
    df_radar_2018 = df_radar_2018.round(decimals=0)

    df_radar_2015 = df_radar_2015[["Borough","Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"]]
    df_radar_2015 = pd.melt(df_radar_2015, id_vars=["Borough"], var_name="Category", value_name="Percent", 
                                value_vars=["Poverty","Unemployment","Air Pollution","Bike Coverage","Smoking","Obesity"])
    df_radar_2015 = df_radar_2015.round(decimals=0)
    
    return df_radar_2022, df_radar_2018, df_radar_2015

def get_measures_stacked():
    df_measures_2022 = pd.read_excel(
       io='data/measures_2022.xlsx',
       sheet_name ='CHP_all_data'
    )
    df_measures_2018 = pd.read_excel(
       io='data/measures_2018.xlsx',
       sheet_name ='CHP_all_data'
    )
    df_measures_2015 = pd.read_excel(
       io='data/measures_2015.xlsx',
       sheet_name ='CHP_all_data'
    )
    
    df_stacked_2022 = df_measures_2022
    df_stacked_2018 = df_measures_2018
    df_stacked_2015 = df_measures_2015

    df_stacked_2022 = df_stacked_2022[["Borough","Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"]]
    #df_stacked_2022 = df_stacked_2022.round(decimals=2)
    df_stacked_2022 = pd.melt(df_stacked_2022, id_vars=["Borough"], var_name="Range", value_name="Percent", 
                                value_vars=["Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"])

    df_stacked_2018 = df_stacked_2018[["Borough","Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"]]
    #df_stacked_2018 = df_stacked_2018.round(decimals=2)
    df_stacked_2018 = pd.melt(df_stacked_2018, id_vars=["Borough"], var_name="Range", value_name="Percent", 
                                value_vars=["Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"])

    df_stacked_2015 = df_stacked_2015[["Borough","Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"]]
    #df_stacked_2015 = df_stacked_2015.round(decimals=2)
    df_stacked_2015 = pd.melt(df_stacked_2015, id_vars=["Borough"], var_name="Range", value_name="Percent", 
                                value_vars=["Age 0 - 17","Age 18 - 24","Age 25 - 44","Age 45 - 64","Age 65 plus"])
    
    return df_stacked_2022, df_stacked_2018, df_stacked_2015

def get_timeline():
    df_timeline = pd.read_csv('data/medianAskingRent_grouped.csv', sep=';')
    return df_timeline

def get_school_loc():
    df_school_loc = pd.read_csv('data/school_locations_2019_2020.csv')
    df_school_loc.rename(columns={"LONGITUDE": "Longitude", "LATITUDE": "Latitude"}, inplace=True)
    return df_school_loc

def load_facility_dataset():
    df_fac = pd.read_csv('data/facilities.csv')
    df_fac = df_fac[["facname","latitude","longitude","facgroup","facsubgrp","factype"]]
    df_fac.rename(columns={"longitude": "Longitude", "latitude": "Latitude"}, inplace=True)
    return df_fac

def get_facilities(df, facgroup = None, facsubgrp = None):   
    if facgroup is not None:
        return df[df['facgroup'] == facgroup]
    elif facsubgrp is not None:
        return df[df['facsubgrp'] == facsubgrp]

    return df

def get_parking_geodata():
    with open('data/Parking.geojson') as f:
        nypd_parking_geo = json.load(f)
    return nypd_parking_geo

def get_hurricane_geodata():
    with open('data/Hurricane_Evac_Zones.geojson') as f:
        nypd_hurricane_geo = json.load(f)
    return nypd_hurricane_geo




