import os
import copy
import time
import datetime
import json
import logging
#import dash

from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
#from dash_bootstrap_templates import load_figure_template
#load_figure_template('LUX')
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

from data_preprocessing import *


logger = logging.getLogger(__name__)

# Static configuration
external_stylesheets = [
    # Dash CSS
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    # Loading screen CSS
    'https://codepen.io/chriddyp/pen/brPBPO.css']

COLORS = {
    'background': '#fff',
    'text': '#000'
}

styles = {
    'pre': {
        'border': 'thin lightgrey solid',
        'overflowX': 'scroll'
    }
}

mapbox_access_token = 'pk.eyJ1Ijoib2JhdXNlIiwiYSI6ImNsZ3lydDJkajBjYnQzaHFjd3VwcmdoZ3oifQ.yHMnUntRqbBXwCmezGo10w'

#bs = 'https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css'
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY]) #dbc.themes.CYBORG


map_categories = ['Environment', 'Public Safety, Emergency Services and Justice', 'Education and Youth', 'Libraries and Cultural Programs', 'Health and Human Services', 'Transportation']

# save data_dict as json file
with open('data_dict.json', 'r') as f:
    data_dict = json.load(f)
with open('data_meta.json', 'r') as f:
    filter_options = json.load(f)

attributes = {
    "shootings": {'OCCUR_DATE': 'Date', 'OCCUR_TIME': 'Time', 'BORO': 'Borough', 'LOC_OF_OCCUR_DESC': 'Location', 'PRECINCT': 'Precinct', 'STATISTICAL_MURDER_FLAG': 'Murdered', 'PERP_AGE_GROUP': 'Offender Age Group', 'PERP_SEX': 'Offender Sex', 'PERP_RACE': 'Offender Ethnicity', 'PERP_AGE_GROUP': 'Offender Age', 'VIC_SEX': 'Victim Sex', 'VIC_RACE': 'Victim Ethnicity'},
    "squirrels": {'Age': 'Age', 'Primary Fur Color': 'Primary Fur Color', 'Highlight Fur Color': 'Highlight Fur Color', 'Location': 'Location', 'Running': 'Running', 'Chasing': 'Chasing', 'Climbing': 'Climbing', 'Eating': 'Eating', 'Foraging': 'Foraging', 'Other Activities': 'Other Activities', 'Kuks': 'Kuks', 'Quaas': 'Quaas', 'Moans': 'Moans', 'Tail flags': 'Tail flags', 'Tail twitches': 'Tail twitches', 'Approaches': 'Approaches', 'Runs from': 'Runs from', 'Other Interactions': 'Other Interactions'},
    "schools": {}
}

# Data loading and preprocessing
borough_mapping = get_borough_mappings()

nyc_parks_geo = get_park_geodata()
data_dict['parks']['data'] = nyc_parks_geo
nypd_precincts_geo = get_nypd_precincts_geodata()
data_dict['nypd_precincts']['data'] = nypd_precincts_geo
community_districts_geo = get_community_districts_geodata()
data_dict['community_districts']['data'] = community_districts_geo


nyc_crime_shootings = get_crime_shootings()
data_dict['shootings']['data'] = nyc_crime_shootings
nyc_crime_arrests = get_crime_arrests()
data_dict['arrests']['data'] = nyc_crime_arrests
data_dict['arrests']['text'] = nyc_crime_arrests['OFNS_DESC']

squirrels = get_squirrels()
data_dict['squirrels']['data'] = squirrels

hospitals = get_hospital_data()
data_dict['hospitals']['data'] = hospitals
data_dict['hospitals']['text'] = hospitals['Facility Name']

car_accidents = get_car_accident_data()
data_dict['car_accidents']['data'] = car_accidents
data_dict['car_accidents']['text'] = car_accidents['CONTRIBUTING FACTOR VEHICLE 1']

nyc_borough_geo = get_borough_geodata()
data_dict['borough']['data'] = nyc_borough_geo
nyc_borough_mapping = get_borough_mappings()
data_dict['borough_labels']['data'] = nyc_borough_mapping
data_dict['borough_labels']['text'] = nyc_borough_mapping['borough_name']


df_air = get_air_quality_data()
air_quality_measures = {
    'air_pollution_pm25': {'measure_name': 'Fine Particulate Matter (PM2.5)', 'time_period': 'Annual Average 2020'},
    'air_pollution_hospitalizations': {'measure_name': 'PM2.5-Attributable Respiratory Hospitalizations (Adults 20 Yrs and Older)', 'time_period': '2015-2017'},    
    'air_toxics': {'measure_name': 'Air Toxics Concentrations- Average Benzene Concentrations', 'time_period': '2011'},
    'air_pollution_ozone': {'measure_name': 'Ozone (O3)', 'time_period': 'Summer 2020'},
    'air_pollution_so2': {'measure_name': 'Sulfur Dioxide (SO2)', 'time_period': 'Winter 2015-16'},
    'air_pollution_no2': {'measure_name': 'Nitrogen Dioxide (NO2)', 'time_period': 'Annual Average 2020'},
    'traffic_density': {'measure_name': 'Traffic Density- Annual Vehicle Miles Traveled', 'time_period': '2016'},
    }
for key, value in air_quality_measures.items():
    df_air_filtered = df_air[(df_air['Name'] == value['measure_name']) & (df_air['Time Period'] == value['time_period'])]
    data_dict[key]['data'] = df_air_filtered
    data_dict[key]['text'] = df_air_filtered['Geo Place Name']
    data_dict[key]['locations'] = df_air_filtered['Geo Join ID']
    data_dict[key]['values'] = df_air_filtered['Data Value']
    data_dict[key]['geodata'] = community_districts_geo

community_districts_geodf = get_community_districts_geodf()
data_dict['community_districts_labels']['data'] = community_districts_geodf
data_dict['community_districts_labels']['data'] = community_districts_geodf
data_dict['community_districts_labels']['text'] = community_districts_geodf['displayname']

df_radar_2022, df_radar_2018, df_radar_2015 = get_measures_radar()
df_stacked_2022, df_stacked_2018, df_stacked_2015 = get_measures_stacked()
df_timeline = get_timeline()

df_schools = get_facilities(facgroup = 'SCHOOLS (K-12)')
data_dict['schools']['data'] = df_schools
data_dict['schools']['text'] = df_schools['facname'] 

df_colleges = get_facilities(facsubgrp = 'COLLEGES OR UNIVERSITIES')
data_dict['colleges']['data'] = df_colleges
data_dict['colleges']['text'] = df_colleges['facname'] 

df_hist_sites = get_facilities(facsubgrp = 'HISTORICAL SITES')
data_dict['hist_sites']['data'] = df_hist_sites
data_dict['hist_sites']['text'] = df_hist_sites['facname'] 

df_youth_services = get_facilities(facgroup = 'YOUTH SERVICES')
data_dict['youth_services']['data'] = df_youth_services
data_dict['youth_services']['text'] = df_youth_services['facname'] 

df_camps = get_facilities(facgroup = 'CAMPS')
data_dict['camps']['data'] = df_camps
data_dict['camps']['text'] = df_camps['facname'] 

df_libraries = get_facilities(facgroup = 'LIBRARIES')
data_dict['libraries']['data'] = df_libraries
data_dict['libraries']['text'] = df_libraries['facname'] 

df_cult = get_facilities(facgroup = 'CULTURAL INSTITUTIONS')
data_dict['cult']['data'] = df_cult
data_dict['cult']['text'] = df_cult['facname'] 

df_hospitals = get_facilities(facsubgrp = 'HOSPITALS AND CLINICS')
data_dict['hospitals']['data'] = df_hospitals
data_dict['hospitals']['text'] = df_hospitals['facname'] 

df_mental = get_facilities(facsubgrp = 'MENTAL HEALTH')
data_dict['mental']['data'] = df_mental
data_dict['mental']['text'] = df_mental['facname'] 

df_residential = get_facilities(facsubgrp = 'RESIDENTIAL HEALTH CARE')
data_dict['residential']['data'] = df_residential
data_dict['residential']['text'] = df_residential['facname'] 

df_senior = get_facilities(facsubgrp = 'SENIOR SERVICES')
data_dict['senior']['data'] = df_senior
data_dict['senior']['text'] = df_senior['facname'] 

df_soup = get_facilities(facsubgrp = 'SOUP KITCHENS AND FOOD PANTRIES')
data_dict['soup']['data'] = df_soup
data_dict['soup']['text'] = df_soup['facname'] 

df_bus = get_facilities(facsubgrp = 'BUS DEPOTS AND TERMINALS')
data_dict['bus']['data'] = df_bus
data_dict['bus']['text'] = df_bus['facname'] 

df_railyards = get_facilities(facsubgrp = 'RAIL YARDS AND MAINTENANCE')
data_dict['railyards']['data'] = df_railyards
data_dict['railyards']['text'] = df_railyards['facname']

df_ports = get_facilities(facsubgrp = 'PORTS AND FERRY LANDINGS')
data_dict['ports']['data'] = df_ports
data_dict['ports']['text'] = df_ports['facname']

df_airports = get_facilities(facsubgrp = 'AIRPORTS AND HELIPORTS')
data_dict['airports']['data'] = df_airports
data_dict['airports']['text'] = df_airports['facname']

df_fireservices = get_facilities(facsubgrp = 'FIRE SERVICES')
data_dict['fireservices']['data'] = df_fireservices
data_dict['fireservices']['text'] = df_fireservices['facname']

df_policeservices = get_facilities(facsubgrp = 'POLICE SERVICES')
data_dict['policeservices']['data'] = df_policeservices
data_dict['policeservices']['text'] = df_policeservices['facname']

df_court = get_facilities(facsubgrp = 'COURTHOUSES AND JUDICIAL')
data_dict['court']['data'] = df_court
data_dict['court']['text'] = df_court['facname']

df_detention = get_facilities(facsubgrp = 'DETENTION AND CORRECTIONAL')
data_dict['detention']['data'] = df_detention
data_dict['detention']['text'] = df_detention['facname']

nypd_parking_geo = get_parking_geodata()
data_dict['parking']['data'] = nypd_parking_geo

nypd_hurricane_geo = get_hurricane_geodata()
data_dict['hurricane']['data'] = nypd_hurricane_geo

mapbox_access_token = 'pk.eyJ1Ijoib2JhdXNlIiwiYSI6ImNsZ3lydDJkajBjYnQzaHFjd3VwcmdoZ3oifQ.yHMnUntRqbBXwCmezGo10w'

fig_map = go.Figure(go.Scattermapbox())

fig_map.update_layout(
    mapbox = {
            'accesstoken': mapbox_access_token,
            #'style': "stamen-terrain",
            'center': { 'lon': -73.935242, 'lat': 40.730610},
            'zoom': 10, 
        },
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        height=800,
    )


fig_map.update_layout(
    plot_bgcolor=COLORS['background'],
    paper_bgcolor=COLORS['background'],
    font_color=COLORS['text']
)

fig_cd_map = go.Figure(go.Scattermapbox())
fig_cd_map.add_trace(go.Scattermapbox(
                    lon = community_districts_geodf.Longitude, lat = community_districts_geodf.Latitude,
                    text=community_districts_geodf['displayname'],
                    mode='text',
                ))
fig_cd_map.update_layout(
    mapbox = {
            'accesstoken': mapbox_access_token,
            #'style': "stamen-terrain",
            'center': { 'lon': -73.935242, 'lat': 40.730610},
            'zoom': 10, 
            'layers': [{
                'source': community_districts_geo,
                'type': "fill", 'below': "traces", 'color': "green", 'opacity': 0.5
                }],
        },
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        height=400,
    )

boro_indicators = get_nyc_borough_indicators()
categories = [
    'Age under 18', 
    'Age 65 & Over',
    'Limited English Proficiency', 
    'Rent Burdened',
    'Poverty Rate',
    'Unemployment Rate',
    'Crime Rate',
]
fig_radar = go.Figure()
for i in range(0, len(boro_indicators)):
    fig_radar.add_trace(go.Scatterpolar(
        r=boro_indicators[categories].iloc[i].values,
        theta=categories,
        fill='toself',
        name=boro_indicators['borough'][i],
        mode='markers',
        visible='legendonly' if boro_indicators['borough'][i] != 'New York City' else None
    ))
fig_radar.update_layout(
  #polar=dict(
  #  radialaxis=dict(
  #    visible=True,
  #    range=[0, 50]
  #  )),
  showlegend=True,
  hovermode="x unified",
  clickmode='event+select'
)
fig_radar_bar = go.Figure(go.Bar())


# Generate Filter Options
@app.callback(
    Output('map-filter', 'children'),
    Input('map-category', 'value'),
    State('map-filter', 'value'))
def set_filter_options(selected_category, selected_filters):
    print("Selected category: ", selected_category)
    
    #return [{'label': i, 'value': i} for i in filter_options[selected_category]].keys() + [{'label': 'All', 'value': 'All'}]
    options = []
    if selected_category is None:
        return options
    else:
        if selected_filters is not None:
            #options += [{'label': filter_options[i]['name'], 'value': i} for i in selected_filters]
            options += [dmc.Chip(filter_options[i]['name'], value=i, variant="outline") for i in selected_filters]
        #options += [{'label': 'All', 'value': 'All'}]
        for key, value in filter_options.items():
            if selected_category == value['category']:
                #options += [{'label': value['name'], 'value': key}]
                options.append(
                    dmc.Chip([
                        DashIconify(
                            icon=value.get('icon', 'fa:circle'),
                            width=17,
                            height=17,
                            inline=True,
                            style={"marginRight": 5},),
                        value['name'], 
                        ],
                        value=key, 
                        variant="outline"
                        )
                    )


    return options


@app.callback(
    Output('map', 'figure'),
    Input('map-filter', 'value'))
def update_map(filter_values):
    print("Filters: {}".format(filter_values))
    print("type: {}".format(type(filter_values)))
    
    layers = []
    center = { 'lon': -73.935242, 'lat': 40.730610}
    zoom = 10
    
    fig_map = go.Figure(go.Scattermapbox())
    
    if filter_values is not None:
        for filter_value in filter_values:
            if filter_options[filter_value].get('connected_to') is not None:
                filter_values.append(filter_options[filter_value]['connected_to'])
                print("Connected to: {}".format(filter_options[filter_value]['connected_to']))
            
            if data_dict[filter_value].get('center') is not None:
                center = data_dict[filter_value]['center']
            
            if data_dict[filter_value].get('zoom') is not None:
                zoom = data_dict[filter_value]['zoom']
            
            if filter_options[filter_value]['type'] == 'polygons':
                data = data_dict[filter_value]['data']
                layers.append(
                    {
                        'source': data,
                        'type': "fill", 
                        'below': "traces", 
                        'color': data_dict[filter_value].get('color'), 
                        'opacity': data_dict[filter_value].get('opacity', 0.8)
                    }
                )
                
            elif filter_options[filter_value]['type'] == 'points':
                print("is points")
                data = data_dict[filter_value]['data']
                fig_map.add_trace(go.Scattermapbox(
                    lon = data.Longitude, lat = data.Latitude,
                    marker = data_dict[filter_value].get('marker_style'),
                    text=data_dict[filter_value].get('text'),
                    mode=data_dict[filter_value].get('mode', 'markers'),
                    name=data_dict[filter_value].get('name'),
                ))
                
            elif filter_options[filter_value]['type'] == 'density':
                print("is density")
                data = data_dict[filter_value]['data']
                fig_map.add_trace(go.Densitymapbox(
                    lon = data.Longitude, lat = data.Latitude,
                    radius=data_dict[filter_value].get('radius',3),
                    colorscale=data_dict[filter_value].get('colorscale', 'hot'),
                    text=data_dict[filter_value].get('text'),
                    hovertext=data_dict[filter_value].get('text'),
                    name=data_dict[filter_value].get('name'),
                    ))
                
            elif filter_options[filter_value]['type'] == 'choropleth':
                print("is chloropeth")
                geodata = data_dict[filter_value]['geodata']
                data = data_dict[filter_value]['data']
                values = data_dict[filter_value].get('values')
                print("len values:", len(values))
                fig_map.add_trace(go.Choroplethmapbox(
                    geojson=geodata,
                    locations=data_dict[filter_value].get('locations'),
                    z=values,
                    zmin=values.min(),
                    zmax=values.min(),
                    colorscale=data_dict[filter_value].get('colorscale', 'hot'),
                    marker_opacity=0.5, marker_line_width=0,
                    name=data_dict[filter_value].get('name'),
                    ))
    
    mapbox_dict = {
            'accesstoken': mapbox_access_token,
            #'style': "stamen-terrain",
            'center': center,
            'zoom': zoom, 'layers': layers}
    
    fig_map.update_layout(
        mapbox = mapbox_dict,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        height=800,
        transition_duration=500,
        showlegend=False
        )
    return fig_map


@app.callback(
    Output('map-click-data', 'children'),
    Input('map', 'clickData'),
    State('map-filter', 'value'))
def display_click_data(clickData, state):
    print("clickData: ", clickData)
    print("state: ", state)
    
    if clickData is None:
        return "nothing selected"
    
    curve_number = clickData['points'][0]['curveNumber']
    point_number = clickData['points'][0]['pointNumber']
    
    for i in state:
        if filter_options[i]['type'] == 'polygons':
            state.remove(i)
    
    selected_dataset = state[curve_number-1]
    
    point_data = data_dict[selected_dataset]['data'].iloc[point_number]

    attributes_list = attributes.get(selected_dataset)
    if attributes_list is not None:
        selected_attributes = attributes_list.keys()
    else:
        attributes_list = {i: i for i in point_data.keys()}
        selected_attributes = point_data.keys()
    
    print("attributes_list: ", attributes_list)
    
    #content = dash_table.DataTable(
    #    columns=[{"name": 'attribute', "id": 'attribute'}, {"name": 'value', "id": 'value'}],
    #    data=[{'attribute': attributes_list[col], 'value': value} for col, value in point_data.items() if col in selected_attributes]
    #)
    header = [html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")]))]
    rows = [html.Tr([html.Td(attributes_list[col]), html.Td(str(value).replace("True", "Yes"))]) for col, value in point_data.items() if col in selected_attributes]
    table = [html.Thead(header), html.Tbody(rows)]
    return table #json.dumps(clickData, indent=2)

@app.callback(
    Output('cd-demographics', 'style'),
    Input('cd-dropdown', 'value'))
def hide_cd_demo(cd):
    if cd is None:
        return {'display': 'none'}
    

demo_ages_cd = get_cd_demographic_data()
cd_indicators = get_cd_indicators()
@app.callback(
    Output('cd-demographics', 'figure'),
    Input('cd-dropdown', 'value'))
def update_cd_demo(cd):
    if cd is None:
        return go.Figure()
    print("selected cd: ", cd)
    filtered_df = demo_ages_cd[demo_ages_cd["cd_number"] == cd]
    #filtered_df.drop(columns=['cd_number'], inplace=True)
    fig = px.bar(
        filtered_df
        #.drop(columns="index")
        .assign(group=lambda d: d["gender"].astype(str)),
        y="age_group",
        x="value",
        facet_col="gender",
        facet_col_spacing=0.1,
        color="gender",
        color_discrete_sequence=["#472323", "#233147"],
        labels=get_cd_demographic_legend()
    )
    fig.update_layout(
        yaxis2={"side": "right", "matches": None, "showticklabels": False},
        yaxis={"side": "right", "showticklabels": True, "title": ""},
        xaxis={"autorange": "reversed", "title": "Population %"},
        xaxis2={"matches": None, "title": "Population %"},
        showlegend=False,
        width=500,
        bargap=0.50,
        margin = {'l':0, 'r':0, 'b':0, 't':0},
    )
    fig.update_traces(width=0.4)
    #fig.for_each_annotation(lambda a: a.update(text=""))
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    #fig.update_traces(texttemplate="%{y}", textposition="inside")
    return fig


#@app.callback(
#    Output('cd-map', 'figure'),
#    Input('cd-dropdown', 'value'))
def update_cd_map(selected_cd):
    if selected_cd is None:
        center = [40.730610, -73.935242]
        zoom = 10
    else:
        center = community_districts_geodf[community_districts_geodf['GEOCODE']==selected_cd][['Latitude', 'Longitude']].values[0].tolist()
        zoom = 12
    fig_cd_map = go.Figure(go.Scattermapbox())
    fig_cd_map.add_trace(go.Scattermapbox(
                        lon = community_districts_geodf.Longitude, lat = community_districts_geodf.Latitude,
                        text=community_districts_geodf['displayname'],
                        mode='text',
                    ))
    print("center: ", center)
    fig_cd_map.update_layout(
        mapbox = {
                'accesstoken': mapbox_access_token,
                #'style': "stamen-terrain",
                'center': { 'lon': center[0], 'lat': center[1]},
                'zoom': zoom, 
                'layers': [{
                    'source': community_districts_geo,
                    'type': "fill", 'below': "traces", 'color': "green", 'opacity': 0.5
                    }],
            },
            margin = {'l':0, 'r':0, 'b':0, 't':0},
            height=400,
        )
    return fig_cd_map

@app.callback(
    Output('cd-indicators', 'figure'),
    Input('cd-dropdown', 'value'))
def update_cd_indicators(selected_cd):
    if selected_cd is None:
        return None
    
    filtered_df = cd_indicators[cd_indicators["cd_number"] == selected_cd]
    
    fig = go.Figure()
    for col in filtered_df.columns[3:]:
        print("col: ", col)
        print("value: ", filtered_df[col].values[0])
        fig.add_trace(go.Indicator(
            mode = "number",
            value = filtered_df[col].values[0],
            title={"text": col},
            #domain = {'x': [0, 0.5], 'y': [0, 0.5]},
            #delta = {'reference': 400, 'relative': True, 'position' : "top"}
        ))
    # set min max y axis
    fig.update_yaxes(range=[1000, 4000])
    return fig


@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value")
)
def update_line_chart(selected_year):
    df = df_timeline
    
    fig = go.Figure()
    
    if selected_year == 20:
        df_filtered = df
        x_axis = 'Date'
        xaxis_label = 'Year'
        yaxis_label = 'Rent'
    else:
        mask = df["Year"] == selected_year
        df_filtered = df[mask]
        x_axis = 'Month Names'
        xaxis_label = 'Month'
        yaxis_label = 'Rent'

    for borough in df_filtered['Borough'].unique():
        df_filtered_borough = df_filtered[df_filtered['Borough'] == borough]
        linewidth = 1
        dash = 'solid'
        if borough == 'New York City':
            linewidth = 4
            dash = 'dash'
        fig.add_trace(go.Scatter(
            x=df_filtered_borough[x_axis], 
            y=df_filtered_borough["Rent"], 
            name=borough, 
            mode='lines',
            connectgaps=True,
            line=dict(width=linewidth, dash=dash),
            ))
      
    fig.update_layout(
        title="Average Rent Prices of 1 Bedroom Apartments",
        xaxis_title = xaxis_label,  
        yaxis_title = yaxis_label,
        title_x=0.5,
        transition_duration=500,
    )  
    return fig

@app.callback(
    Output("stacked", "figure"),
    Input("slider", "value")
)
def update_stacked(selected_year):
    df_2022 = df_stacked_2022
    df_2018 = df_stacked_2018
    df_2015 = df_stacked_2015
    
    if selected_year == 3:
        fig = px.bar(data_frame= df_2022, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                     title="Distribution of Age")
    elif selected_year == 2:
        fig = px.bar(data_frame= df_2018, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                     title="Distribution of Age")
    else:
        fig = px.bar(data_frame= df_2015, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                     title="Distribution of Age")
    
    fig.update_layout(
        title_x=0.5,
    )
    return fig


@app.callback(
    Output("radar", "figure"),
    Input("slider", "value")
)
def update_radar(selected_year):
    df_2022 = df_radar_2022
    df_2018 = df_radar_2018
    df_2015 = df_radar_2015
    
    if selected_year == 3:
        fig = px.line_polar(df_2022, r="Percent", 
                    theta="Category", 
                    color="Borough",
                    line_close=True,
                    line_shape="spline",
                    hover_name="Borough",
                    hover_data={"Borough":False},
                    markers=True,
                    range_r=[0,35],
                    direction="clockwise",
                    start_angle=45,
                    title="Detailed Overview of Boroughs"
                   )
    elif selected_year == 2:
        fig = px.line_polar(df_2018, r="Percent", 
                    theta="Category", 
                    color="Borough",
                    line_close=True,
                    line_shape="spline",
                    hover_name="Borough",
                    hover_data={"Borough":False},
                    markers=True,
                    range_r=[0,35],
                    direction="clockwise",
                    start_angle=45,
                    title="Detailed Overview of Boroughs"
                   )
    else:
        fig = px.line_polar(df_2015, r="Percent", 
                    theta="Category", 
                    color="Borough",
                    line_close=True,
                    line_shape="spline",
                    hover_name="Borough",
                    hover_data={"Borough":False},
                    markers=True,
                    range_r=[0,35],
                    direction="clockwise",
                    start_angle=45,
                    title="Detailed Overview of Boroughs",
                   )
    fig.update_layout(
        title_x=0.5,
    )
    return fig


dropdown_options_cd = [{"label": f"{value['GEONAME']} ({value['GEOCODE']})", "value": value['GEOCODE']} for i, value in community_districts_geodf.iterrows()]

@app.callback(
    Output("drawer-data-details", "children"),
    Input("map-filter", "value"),
    #prevent_initial_call=True,
)
def drawer_data_details(filter_values):
    content = []
    if filter_values is None:
        content.append(html.P("No data selected. Please select data from the filter options."))
    else:
        for filter_value in filter_values:
            content += [
                dmc.Text(filter_options[filter_value].get('name'), size="xl"),
                dmc.Text('Data Description:', weight=500),
                dmc.Text(filter_options[filter_value].get('description')),
                dmc.Text(f"Data period: {filter_options[filter_value].get('data_period')}", color='dimmed'),
                dmc.Text(f"Source: <a href={filter_options[filter_value].get('source')}>{filter_options[filter_value].get('source')}</a>", size='sm'),
                dmc.Divider(variant="solid"),
            ]
    return content

@app.callback(
    Output("drawer-data-details", "opened"),
    Input("data-details-button", "n_clicks"),
    prevent_initial_call=True,
)
def drawer_demo(n_clicks):
    return True

# App layout
app.layout = dbc.Container([
    dbc.Container([
        dbc.Row([
            #html.Img(src=app.get_asset_url('images/new-york-city-skyline-silhouette.png'), className='logo'),
            html.H1(
                children='New York Smart City Dashboard',
                style={
                    'textAlign': 'center',
                    #'color': COLORS['text']
                }
            ),
            
        ]),
        dbc.Row(
            
            html.P(
                children='by Ole Bause and Alexander Barkov',
                style={
                    'textAlign': 'center',
                    #'color': COLORS['text']
                    },
            className='subtitle'
            ), 
            
        ),
    ], class_name="title-bar", fluid=True),
    dbc.Container([
    
        dbc.Row([
            html.Hr(),

            html.H3(
                children='Map of NYC',
                style={
                    'textAlign': 'center',
                    'color': COLORS['text']
                }
            ),    
        ]),
        
        dbc.Row([
            dbc.Col([
                dmc.Select(
                    label="Select category",
                    placeholder="Select one",
                    id="map-category",
                    value="ng",
                    data=[{'value': i, 'label': i} for i in map_categories],
                    clearable=True,
                    icon=DashIconify(icon="bxs:category"),
                    style={"width": 350, "marginBottom": 10},
                ),
            ], width=3),
            dbc.Col([
                dmc.Text("Select a filter", weight=500),
                dmc.ChipGroup(
                    id="map-filter",
                    multiple=True,
                    #label="Select a filter",
                    #description="This is anonymous",
                    #orientation="horizontal",
                    #offset="md",
                    #mb=10,
                    className="map-filter",
                ),
                dmc.Text(id="chips-values-output"),
            ], width=9), #style={'padding': 10, 'flex': 1})
        ]), #style={'display': 'flex', 'flex-direction': 'row'}),
        
        dbc.Row([
            dbc.Col(
                dcc.Graph(
                    id='map',
                    figure=fig_map,
                    className='map',
                ),
                width=10
            ),
            dbc.Col([
                html.H3("Detailed Information"),
                dmc.Button("Show dataset details", id="data-details-button"),
                html.H6("Click on any data point to show detailed information about this point"),
                html.Div(id='map-click-data'),
                dmc.Drawer(
                    title="Data Details",
                    id="drawer-data-details",
                    padding="md",
                    zIndex=10000,
                    position="right",
                ),
            ], width=2),
                
        ]),
        dmc.Paper(
            children=[
                dbc.Row(
                    dbc.Col(
                        dcc.Graph(id="graph")
                    )
                ),
                dbc.Row([
                        dbc.Col([
                            dcc.Dropdown(
                                id="dropdown",
                                options=[
                                    {"label": "Complete Timeline", "value": 20},
                                    {"label": "2010", "value": 2010},
                                    {"label": "2011", "value": 2011},
                                    {"label": "2012", "value": 2012},
                                    {"label": "2013", "value": 2013},
                                    {"label": "2014", "value": 2014},
                                    {"label": "2015", "value": 2015},
                                    {"label": "2016", "value": 2016},
                                    {"label": "2017", "value": 2017},
                                    {"label": "2018", "value": 2018},
                                    {"label": "2019", "value": 2019},
                                    {"label": "2020", "value": 2020},
                                    {"label": "2021", "value": 2021},
                                    {"label": "2022", "value": 2022},
                                    {"label": "2023", "value": 2023},
                                ],
                                value=20,
                            )], width=4
                        ),
                    ], justify="center"
                ),
            ],
            shadow="xl",
            p='xs',
            radius='md'
        ),
        html.Hr(style={'marginBottom': 50, 'color': 'rgba(0, 0, 0, 0)'}),
        dmc.Paper(
            children=[
                
                
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(id="stacked")
                    ], width=6),
                    dbc.Col([
                        dcc.Graph(id="radar")
                    ], width=6),
                ]),
                dbc.Row(
                    dbc.Col(
                    dcc.Slider(1, 3, 1,
                                value=2,
                                id='slider',
                                marks={
                                    1: {'label': '2015', 'style': {'color': '#77b0b1'}},
                                    2: {'label': '2018', 'style': {'color': '#77b0b1'}},
                                    3: {'label': '2022', 'style': {'color': '#77b0b1'}},
                                }, included=False
                        ), width={"size": 5}
                    ), justify="center"
                ),
            ], shadow="xl", p='xs', radius='md'
        ),
        html.Hr(style={'marginBottom': 50, 'color': 'rgba(0, 0, 0, 0)'}),
        dmc.Paper(
            children=[
            dbc.Row([
                dbc.Col([
                    html.Br(),
                    html.Label('Category'),
                    dcc.Dropdown(dropdown_options_cd,
                                #value=dropdown_options_cd[0],
                                #multi=True,
                                id='cd-dropdown'
                                ), #style={'padding': 10, 'flex': 1}  
                ], width=4),
            ]),
            dbc.Row([
                dbc.Col([
                    dcc.Graph(
                        id='cd-map',
                        figure=fig_cd_map
                    ),
                    
                ], width=4),
                dbc.Col([
                    dcc.Graph(
                        id='cd-demographics',
                        #figure=fig_cd_map
                    ),
                ], width=4),
                dbc.Col([
                    dcc.Graph(id="cd-indicators", figure=go.Figure().add_trace(go.Indicator(
                        mode = "number",
                        value = 0,))),
                ], width=4),
            ]),
            ], shadow="xl", p='xs', radius='md'
        ),
        html.Hr(style={'marginBottom': 50, 'color': 'rgba(0, 0, 0, 0)'}),
    ],fluid=True,),
], class_name="main-container",fluid=True,) #fluid=True if you want your Container to fill available horizontal space and resize fluidly.




if __name__ == '__main__':
    app.run_server(debug=True, processes=1, threaded=False)