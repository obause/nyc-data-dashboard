import os
import copy
import time
import datetime
import json
import logging

from dash import Dash, dcc, html, Input, Output
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

data_dict = {
    "shootings": {"marker_style": marker_style_shooting, "text": "Shooting Incident"},
    "arrests": {"marker_style": marker_style_arrests, "text": "Arrest", "colorscale": 'Reds', "radius": 2},
    "nypd_precincts": {"color": "#2596be"},
    "community_districts": {"color": "#f8ff99"},
    "air_pollution": {"colorscale": ['green', 'orange', 'red', 'red'], "zmin": 0, "zmax": 7,},
    "hospitals": {"marker_style": marker_style_hospitals, "text": "Hospital"},
    "schools": {},
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
    "schools": {"name": "Schools", "category": "Social/Health"},
    "parks": {"name": "Parks", "category": "Environment", "type": "polygons"},
    "borough": {"name": "Boroughs", "category": "Environment", "type": "polygons", "connected_to": "borough_labels"},
    "borough_labels": {"name": "Boroughs", "category": "hidden", "type": "points"},
    "squirrels": {"name": "Squirrels", "category": "Environment", "type": "points"},
    "car_accidents": {"name": "Car Accidents", "category": "Crime", "type": "density" },
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

air_quality_geo = get_air_quality_data()
data_dict['air_pollution']['data'] = air_quality_geo

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

#@app.callback(
#    Output('radar-bar-chart', 'figure'),
#    Input('radar-chart', 'clickData'))
def update_radar_bar_chart(clickData):
    fig_radar_bar = go.Figure(go.Bar())
    if clickData is None:
        return ""
    #print("clickData: ", clickData)
    selected_indicator = clickData['points'][0]['theta']
    print("selected_indicator: ", selected_indicator)
    fig_radar_bar.add_trace(go.Bar(
        y=indicators['Poverty Rate'],
        x=indicators['borough'],
        text=indicators[selected_indicator],
    ))
    fig_radar_bar.update_layout(
        title=selected_indicator,
        xaxis_tickfont_size=14,
        yaxis=dict(
            title='Percentage %',
            titlefont_size=16,
            tickfont_size=14,
        ),
        barmode='group',
        bargap=0.0, # gap between bars of adjacent location coordinates.
        bargroupgap=0.0 # gap between bars of the same location coordinate.
    )
    fig_radar_bar.update_layout(
    showlegend=False,
    #hovermode="y unified",
    )
    return fig_radar_bar


@app.callback(
    Output('click-data', 'children'),
    Input('radar-chart', 'clickData'))
def display_click_data(clickData):
    text_values = ""
    if clickData is None:
        return ""
    for i in range(0, len(indicators)):
        #if indicators['borough'][i] == clickData['points'][0]['curveNumber']:
        #    selected_category_data[indicators['borough'][i]] = indicators[categories].iloc[i].values
        if i == clickData['points'][0]['curveNumber']:
            text_values += f"""
    **{indicators['borough'][i]}: {indicators[clickData['points'][0]['theta']].iloc[i]}**
            """
        else:
            text_values += f"""
    {indicators['borough'][i]}: {indicators[clickData['points'][0]['theta']].iloc[i]}
            """
    text = f"""
    ##### {clickData['points'][0]['theta']}
    {text_values}
    """
    #return json.dumps(clickData, indent=2)
    print(clickData)
    return text

markdown_text = '''
##### Dash and Markdown

Dash apps can be written in Markdown.
Dash uses the [CommonMark](http://commonmark.org/)
specification of Markdown.
Check out their [60 Second Markdown Tutorial](http://commonmark.org/help/)
if this is your first introduction to Markdown!
'''

# App layout
app.layout = html.Div(style={'backgroundColor': COLORS['background']}, children=[
    html.H1(
        children='New York Smart City Dashboard',
        style={
            'textAlign': 'center',
            'color': COLORS['text']
        }
    ),
    html.P(
        children='by Ole Bause and Alexander Barkov',
        style={
            'textAlign': 'center',
            'color': COLORS['text']
        },
        className='lead'
    ),
    
    html.Hr(),

    html.H3(
        children='Map of NYC',
        style={
            'textAlign': 'center',
            'color': COLORS['text']
        }
    ),
    
    html.Div([
        html.Div(children=[
            html.Br(),
            html.Label('Category'),
            dcc.Dropdown(['Environment', 'Social/Health', 'Crime'],
                        ['Environment'],
                        multi=True,
                        id='map-category'
                        ),
        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Filter'),
            dcc.Checklist(
                        id='map-filter',
                        inline=True
            ),
        ], style={'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    
    dcc.Graph(
        id='map',
        figure=fig_map
    ),

    html.Div(className='container', children=[
        html.Div(className='row', children=[
            html.H3(
                children='Radar Chart',
                style={
                    'textAlign': 'center',
                    'color': COLORS['text']
                }
            ),
            html.P(
                children='Beischreibung zum Radar Chart',
                style={
                    'textAlign': 'center',
                    'color': COLORS['text']
                },
                className='lead'
            ),
        ]),
        html.Div(className='row', children=[
            html.Div([
                dcc.Graph(
                    id='radar-chart',
                    figure=fig_radar
                ),
            ], className='col-sm-8'),

            html.Div([
                dcc.Markdown("""
                    **Data**
                """, id='click-data'),
            # html.P(id='click-data')#, style=styles['pre']),
            ], className='col-sm-2'),

            #html.Div(className='row', children=[
            #    html.Div([
            #        dcc.Graph(
            #            id='radar-bar-chart',
            #            figure=fig_radar_bar
            #        ),
            #    ], className='col-sm-6'),
            #]),
        ]),
        
    ]),
    
    html.Div(children='Dash: A web application framework for your data.', style={
        'textAlign': 'center',
        'color': COLORS['text']
    }),

    
    html.Div([
        dcc.Markdown(children=markdown_text)
    ]),
    
    html.H3(
        children='Dash Controls',
        style={
            'textAlign': 'center',
            'color': COLORS['text']
        }
    ),
    
    html.Div([
        html.Div(children=[
            html.Label('Dropdown'),
            dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),

            html.Br(),
            html.Label('Multi-Select Dropdown'),
            dcc.Dropdown(['New York City', 'Montréal', 'San Francisco'],
                        ['Montréal', 'San Francisco'],
                        multi=True),

            html.Br(),
            html.Label('Radio Items'),
            dcc.RadioItems(['New York City', 'Montréal', 'San Francisco'], 'Montréal'),
        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Checkboxes'),
            dcc.Checklist(['New York City', 'Montréal', 'San Francisco'],
                        ['Montréal', 'San Francisco']
            ),

            html.Br(),
            html.Label('Text Input'),
            dcc.Input(value='MTL', type='text'),

            html.Br(),
            html.Label('Slider'),
            dcc.Slider(
                min=0,
                max=9,
                marks={i: f'Label {i}' if i == 1 else str(i) for i in range(1, 6)},
                value=5,
            ),
        ], style={'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'})
])

if __name__ == '__main__':
    app.run_server(debug=True, processes=1, threaded=False)
