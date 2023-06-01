import os
import copy
import time
import datetime
import json

from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

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

# Data loading and preprocessing
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

df_exports = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

df_life = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

borough_mapping = pd.DataFrame({
    "borough_name": ["Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"],
    "boro_code": [1, 2, 3, 4, 5],
    "boro_short1": ["M", "X", "B", "Q", "R"],
    "boro_short2": ["M", "B", "K", "Q", "S"],
    "lat": [40.776676,40.837048,40.650002,40.742054,40.579021],
    "lon": [-73.971321,-73.865433,-73.949997,-73.769417, -74.151535]
})

with open('data/Parks_Properties.geojson') as f:
    nycParksGeo = json.load(f)

nypd_arrests_2022 = pd.read_csv('data/crime/arrests_2022.csv')
date = nypd_arrests_2022['ARREST_DATE'].str.split("/", n = 3, expand = True)
nypd_arrests_2022['year'] = date[2].astype('int32')
nypd_arrests_2022['day'] = date[1].astype('int32')
nypd_arrests_2022['month'] = date[0].astype('int32')
nypd_shootings = pd.read_csv('data/crime/NYPD_Shooting_Incident_Data__Historic_.csv')
nypd_shootings['OCCUR_DATE'] = pd.to_datetime(nypd_shootings['OCCUR_DATE'])
nypd_shootings['YEAR'] = pd.DatetimeIndex(nypd_shootings['OCCUR_DATE']).year
nypd_shootings_2022 = nypd_shootings[nypd_shootings['YEAR'] == 2022]
with open('data/crime/Police_Precincts.geojson') as f:
    nypd_precincts_geo = json.load(f)


marker_style_shooting = dict(
            size=8,
            color='rgb(255, 0, 0)',
            opacity=0.8
        )    

marker_style_arrests = dict(
            size=6,
            color='rgb(0, 255, 0)',
            symbol='bus',
            opacity=1
)

mapbox_access_token = 'pk.eyJ1Ijoib2JhdXNlIiwiYSI6ImNsZ3lydDJkajBjYnQzaHFjd3VwcmdoZ3oifQ.yHMnUntRqbBXwCmezGo10w'

fig = go.Figure()

fig.add_trace(go.Scattermapbox(
    mode = "markers",
    lon = nypd_shootings_2022.Longitude, lat = nypd_shootings_2022.Latitude,
    marker = marker_style_shooting,
    text=f"Shooting Incident" # <br>Occur date: {nypd_shootings_2022.OCCUR_DATE}<br>Precinct: {nypd_shootings_2022.PRECINCT}<br>Age group: {nypd_shootings_2022.PERP_AGE_GROUP}<br>Sex: {nypd_shootings_2022.PERP_SEX}<br>Race: {nypd_shootings_2022.PERP_RACE}<br>"
    ))

#fig.update_traces(cluster=dict(enabled=True))

#fig.add_trace(go.Densitymapbox(
#    lon = nypd_arrests_2022.Longitude, lat = nypd_arrests_2022.Latitude,
#    radius=3,
#    ))



fig.update_layout(
    mapbox = {
        'style': "stamen-terrain",
        'center': { 'lon': -73.92969252236846, 'lat': 40.73090468938098},
        'zoom': 10, 'layers': [{
            'source': nypd_precincts_geo,
            'type': "fill", 'below': "traces", 'color': "#2596be", 'opacity': 0.8}]},
    margin = {'l':0, 'r':0, 'b':0, 't':0})


fig.update_layout(
    plot_bgcolor=COLORS['background'],
    paper_bgcolor=COLORS['background'],
    font_color=COLORS['text']
)

fig_life = px.scatter(df_life, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)

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

@app.callback(
    Output('click-data', 'children'),
    Input('radar-chart', 'clickData'))
def display_click_data(clickData):
    text_values = ""
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
                        multi=True),
        ], style={'padding': 10, 'flex': 1}),

        html.Div(children=[
            html.Label('Filter'),
            dcc.Checklist(['Parks', 'Bla', 'Blabla'],
                        ['Parks']
            ),
        ], style={'padding': 10, 'flex': 1})
    ], style={'display': 'flex', 'flex-direction': 'row'}),
    
    dcc.Graph(
        id='map',
        figure=fig
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
            ], className='col-sm-4'),

            
        ]),
    ]),
    
    html.Div(children='Dash: A web application framework for your data.', style={
        'textAlign': 'center',
        'color': COLORS['text']
    }),

    dcc.Graph(
        id='life-exp-vs-gdp',
        figure=fig_life
    ),
    
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
