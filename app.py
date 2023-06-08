import os
import copy
import time
import datetime
import json
import logging

from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc

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

#app = Dash(__name__, external_stylesheets=external_stylesheets)
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])
#server = app.server



marker_style_shooting = dict(
            size=8,
            color='rgb(255, 0, 0)',
            opacity=0.8
        )    

marker_style_arrests = dict(
            size=6,
            color='rgb(0, 255, 0)',
            #symbol='bus',
            opacity=1
)

marker_style_squirrels = dict(
            size=4,
            color='orange',
            opacity=1
)

marker_style_hospitals = dict(
            size=8,
            color='rgb(0, 0, 255)',
            opacity=1
)

marker_style_cars = dict(
            size=6,
            color='black',
            opacity=1
)

marker_style_schools = dict(
            size=6,
            color='yellow',
            opacity=1
)

data_dict = {
    "shootings": {"marker_style": marker_style_shooting, "text": "Shooting Incident"},
    "arrests": {"marker_style": marker_style_arrests, "text": "Arrest", "colorscale": 'Reds', "radius": 2},
    "nypd_precincts": {"color": "#2596be"},
    "community_districts": {"color": "#f8ff99"},
    "air_pollution": {"colorscale": ['green', 'orange', 'red', 'red'], "zmin": 0, "zmax": 7,},
    "hospitals": {"marker_style": marker_style_hospitals, "text": "Hospital"},
    "schools": {"marker_style": marker_style_schools, "text": "School"},
    "parks": {"color": "#105200"},
    "borough": {"color": "white"},
    "borough_labels": {"mode": "text", "type": "points"},
    "squirrels": {"marker_style": marker_style_squirrels, "text": "Squirrel", "color": "orange", "center": {"lat": 40.78108498, "lon": -73.96715340}, 'zoom': 14},
    "car_accidents": {"marker_style": marker_style_cars, "text": "Car Accident", "colorscale": 'Reds', "radius": 2},
}

filter_options = {
    "shootings": {"name": "Shootings", "category": "Crime", "type": "points"},
    "arrests": {"name": "Arrests", "category": "Crime", "type": "density"},
    "nypd_precincts": {"name": "NYPD Precincts", "category": "Crime", "type": "polygons"},
    "community_districts": {"name": "Community Districts", "category": "Social/Health", "type": "polygons"},
    "air_pollution": {"name": "Air Pollution", "category": "Social/Health", "type": "choropleth"},
    "hospitals": {"name": "Hospitals", "category": "Social/Health", "type": "points"},
    "schools": {"name": "Schools", "category": "Social/Health", "type": "points"},
    "parks": {"name": "Parks", "category": "Environment", "type": "polygons"},
    "borough": {"name": "Boroughs", "category": "Environment", "type": "polygons", "connected_to": "borough_labels"},
    "borough_labels": {"name": "Boroughs", "category": "hidden", "type": "points"},
    "squirrels": {"name": "Squirrels", "category": "Environment", "type": "points"},
    "car_accidents": {"name": "Car Accidents", "category": "Crime", "type": "density" },
}

attributes = {
    "shootings": {'OCCUR_DATE': 'Date', 'OCCUR_TIME': 'Time', 'BORO': 'Borough', 'LOC_OF_OCCUR_DESC': 'Location', 'PRECINCT': 'Precinct', 'STATISTICAL_MURDER_FLAG': 'Murdered', 'PERP_AGE_GROUP': 'Offender Age Group', 'PERP_SEX': 'Offender Sex', 'PERP_RACE': 'Offender Ethnicity', 'PERP_AGE_GROUP': 'Offender Age', 'VIC_SEX': 'Victim Sex', 'VIC_RACE': 'Victim Ethnicity'},
    "squirrels": {'Age': 'Age', 'Primary Fur Color': 'Primary Fur Color', 'Highlight Fur Color': 'Highlight Fur Color', 'Location': 'Location', 'Running': 'Running', 'Chasing': 'Chasing', 'Climbing': 'Climbing', 'Eating': 'Eating', 'Foraging': 'Foraging', 'Other Activities': 'Other Activities', 'Kuks': 'Kuks', 'Quaas': 'Quaas', 'Moans': 'Moans', 'Tail flags': 'Tail flags', 'Tail twitches': 'Tail twitches', 'Approaches': 'Approaches', 'Runs from': 'Runs from', 'Other Interactions': 'Other Interactions'}
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

multipolygon_json, pd_by_cm = get_air_quality_data(measure_name='Fine Particulate Matter (PM2.5)')
data_dict['air_pollution']['data'] = pd_by_cm
data_dict['air_pollution']['text'] = pd_by_cm['Geo Place Name']
data_dict['air_pollution']['locations'] = pd_by_cm['Geo Join ID']
data_dict['air_pollution']['values'] = pd_by_cm['Data Value']
data_dict['air_pollution']['geodata'] = community_districts_geo

df_radar_2022, df_radar_2018, df_radar_2015 = get_measures_radar()
df_stacked_2022, df_stacked_2018, df_stacked_2015 = get_measures_stacked()
df_timeline = get_timeline()

df_school_loc = get_school_loc()
data_dict['schools']['data'] = df_school_loc
data_dict['schools']['text'] = df_school_loc['location_name']



mapbox_access_token = 'pk.eyJ1Ijoib2JhdXNlIiwiYSI6ImNsZ3lydDJkajBjYnQzaHFjd3VwcmdoZ3oifQ.yHMnUntRqbBXwCmezGo10w'

fig_map = go.Figure(go.Scattermapbox())

#fig.add_trace(go.Scattermapbox(
#    mode = "markers",
#    lon = nyc_crime_shootings.Longitude, lat = nyc_crime_shootings.Latitude,
#    marker = marker_style_shooting,
#    text=f"Shooting Incident" # <br>Occur date: {nypd_shootings_2022.OCCUR_DATE}<br>Precinct: {nypd_shootings_2022.PRECINCT}<br>Age group: {nypd_shootings_2022.PERP_AGE_GROUP}<br>Sex: {nypd_shootings_2022.PERP_SEX}<br>Race: {nypd_shootings_2022.PERP_RACE}<br>"
#    ))

#fig.update_traces(cluster=dict(enabled=True))

#fig.add_trace(go.Densitymapbox(
#    lon = nypd_arrests_2022.Longitude, lat = nypd_arrests_2022.Latitude,
#    radius=3,
#    ))



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

indicators = get_nyc_borough_indicators()
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
for i in range(0, len(indicators)):
    fig_radar.add_trace(go.Scatterpolar(
        r=indicators[categories].iloc[i].values,
        theta=categories,
        fill='toself',
        name=indicators['borough'][i],
        mode='markers',
        visible='legendonly' if indicators['borough'][i] != 'New York City' else None
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
    Output('map-filter', 'options'),
    Input('map-category', 'value'))
def set_filter_options(selected_category):
    print("Selected category: ", selected_category)
    
    #return [{'label': i, 'value': i} for i in filter_options[selected_category]].keys() + [{'label': 'All', 'value': 'All'}]
    options = []
    if len(selected_category) == 0:
        return options
    elif len(selected_category) >= 1:
        options += [{'label': 'All', 'value': 'All'}]
        for cat in selected_category:
            for key, value in filter_options.items():
                if cat == value['category']:
                    options += [{'label': value['name'], 'value': key}]

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
                    marker_opacity=0.5, marker_line_width=0
                    ))
                
    fig_map.update_layout(
        mapbox = {
            'accesstoken': mapbox_access_token,
            #'style': "stamen-terrain",
            'center': center,
            'zoom': zoom, 'layers': layers},
        margin = {'l':0, 'r':0, 'b':0, 't':0},
        height=800,
        transition_duration=500,
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
    
    content = dash_table.DataTable(
        columns=[{"name": 'attribute', "id": 'attribute'}, {"name": 'value', "id": 'value'}],
        data=[{'attribute': attributes_list[col], 'value': value} for col, value in point_data.items() if col in selected_attributes]
    )
    return content #json.dumps(clickData, indent=2)

@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value")
)
def update_line_chart(selected_year):
    df = df_timeline
    
    if selected_year == 20:
        fig = px.line(df, x="Date", y="Miete", color='Borough', title='Average Rent Prices Of 1 Bedroom Apartments')
        xaxis_label = 'Year'
        yaxis_label = 'Rent'
        
    else:
        mask = df["Jahr"] == selected_year
        fig = px.line(df[mask], x="Monate", y="Miete", color='Borough', title='Average Rent Prices Of 1 Bedroom Apartments')
        xaxis_label = 'Month'
        yaxis_label = 'Rent'

    fig.update_yaxes(range=[500, 4500]) 
    fig.update_traces(connectgaps=True, selector=dict(type='line'))
    fig.update_layout(
        xaxis_title = xaxis_label,  
        yaxis_title = yaxis_label,
        title_x=0.5
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
        title_x=0.5
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
        title_x=0.5
    )
    return fig



markdown_text = '''
##### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''

# App layout
app.layout = dbc.Container([
    dbc.Row(
        html.H1(
            children='New York Smart City Dashboard',
            style={
                'textAlign': 'center',
                'color': COLORS['text']
            }
        ),
    ),
    dbc.Row(
        html.P(
            children='by Ole Bause and Alexander Barkov',
            style={
                'textAlign': 'center',
                'color': COLORS['text']
                },
           className='lead'
        ),      
    ),
    
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
            html.Br(),
            html.Label('Category'),
            dcc.Dropdown(['Environment', 'Social/Health', 'Crime'],
                         ['Environment'],
                         multi=True,
                         id='map-category'
                         ), #style={'padding': 10, 'flex': 1}  
        ]),
        dbc.Col([
            html.Label('Filter'),
            dcc.Checklist(
                        id='map-filter',
                        inline=True
            ),    
        ]), #style={'padding': 10, 'flex': 1})
    ]), #style={'display': 'flex', 'flex-direction': 'row'}),
    dbc.Row([
        dbc.Col(
            dcc.Graph(
                id='map',
                figure=fig_map
            ),
            width=10
        ),
        dbc.Col([
            html.H3("Detailed Information"),
            html.H6("Click on any data point to show detailed information about this point"),
            html.Div(id='map-click-data'),
        ], width=2),
            
    ]),
    dbc.Row(
        dbc.Col(
            dcc.Graph(id="graph")
        )
    ),
    dbc.Row([
            dbc.Col(
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
                ), width={"size": 2, "offset": 0}
            ),
        ], className="mt-4",
    ),
    
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
            ), width={"size": 5, "offset": 4}
        )
    ),
    
    ],fluid=True,) #fluid=True if you want your Container to fill available horizontal space and resize fluidly.



if __name__ == '__main__':
    app.run_server(debug=True, processes=1, threaded=False)
