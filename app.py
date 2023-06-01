import os
import copy
import time
import datetime
import json

from dash import Dash, dcc, html, Input, Output

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

mapbox_access_token = 'pk.eyJ1Ijoib2JhdXNlIiwiYSI6ImNsZ3lydDJkajBjYnQzaHFjd3VwcmdoZ3oifQ.yHMnUntRqbBXwCmezGo10w'

app = Dash(__name__, external_stylesheets=external_stylesheets)
#server = app.server

# Data loading and preprocessing
df = pd.DataFrame({
    "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
    "Amount": [4, 1, 2, 2, 4, 5],
    "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
})

df_exports = pd.read_csv('https://gist.githubusercontent.com/chriddyp/c78bf172206ce24f77d6363a2d754b59/raw/c353e8ef842413cae56ae3920b8fd78468aa4cb2/usa-agricultural-exports-2011.csv')

df_life = pd.read_csv('https://gist.githubusercontent.com/chriddyp/5d1ea79569ed194d432e56108a04d188/raw/a9f9e8076b837d541398e999dcbac2b2826a81f8/gdp-life-exp-2007.csv')

with open('data/Parks_Properties.geojson') as f:
    nycParksGeo = json.load(f)

fig = go.Figure(go.Scattermapbox(
    mode = "markers",
    lon = [-73.935242], lat = [40.730610], # 40.730610, -73.935242
    marker = {'size': 20, 'color': ["cyan"]}))

fig.update_layout(
    mapbox = {
        'style': "stamen-terrain",
        'center': { 'lon': -73.92969252236846, 'lat': 40.73090468938098},
        'zoom': 10, 'layers': [{
            'source': nycParksGeo,
            'type': "fill", 'below': "traces", 'color': "green"}]},
    margin = {'l':0, 'r':0, 'b':0, 't':0})

fig.update_layout(
    plot_bgcolor=COLORS['background'],
    paper_bgcolor=COLORS['background'],
    font_color=COLORS['text']
)

fig_life = px.scatter(df_life, x="gdp per capita", y="life expectancy",
                 size="population", color="continent", hover_name="country",
                 log_x=True, size_max=60)


categories = ['Crime Rate', 'Poverty', 'Education', 'Traffic', 'Housing']

fig_radar = go.Figure()

fig_radar.add_trace(go.Scatterpolar(
      r=[
        0.243243, 1, 2, 2, 3
      ],
      theta=categories,
      fill='toself',
      name='Bronx'
))
fig_radar.add_trace(go.Scatterpolar(
      r=[4, 3, 2.5, 1, 2],
      theta=categories,
      fill='toself',
      name='Brooklyn'
))

fig_radar.update_layout(
  polar=dict(
    radialaxis=dict(
      visible=True,
      range=[0, 5]
    )),
  showlegend=True
)

markdown_text = '''
### Dash and Markdown

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

    html.Div(children='by Ole Bause and Alexander Barkov', style={
        'textAlign': 'center',
        'color': COLORS['text']
    }),
    
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
            html.Label('Catergory'),
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
        id='radar-chart',
        figure=fig_radar
    ),
    
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
