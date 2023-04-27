# Import packages
from dash import Dash, html
from dash import dcc        # Dash Core Components um interaktive Elemente zu erstellen    
from dash import dash_table # Dash Table um die Daten in einer Tabelle darzustellen
from dash import callback, Output, Input # Dash Callbacks um die Interaktionen zu verwalten

import pandas as pd
import plotly.express as px

# Daten herunterladen und einlesen in dataframe
df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/gapminder2007.csv')
# Alternativ Lokale Datei einlesen
# df = pd.read_csv('data/gapminder2007.csv')

# Set the stylesheet argument to the URL of your custom stylesheet
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
# Initialize the app
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
# html.Div() ist ein Container, der die Elemente in der App enthält
# html.Div() kann auch mehrere Elemente enthalten
app.layout = html.Div([
    html.Div(className='row', children='My First App with Data, Graph, and Controls',
             style={'textAlign': 'center', 'color': 'blue', 'fontSize': 30}), # Titel der App
    html.Hr(), # Horizontale Linie
    html.Div(className='row', children=[
        dcc.RadioItems(options=['pop', 'lifeExp', 'gdpPercap'],
                       value='lifeExp',
                       inline=True,
                       id='my-radio-buttons-final')
    ]), # Radio Buttons
    html.Div(className='row', children=[
        html.Div(className='six columns', children=[
            dash_table.DataTable(data=df.to_dict('records'), page_size=11, style_table={'overflowX': 'auto'}) # Tabelle
        ]),
        html.Div(className='six columns', children=[
            dcc.Graph(figure={}, id='histo-chart-final') # Histogramm
        ])
    ])
])

# Callback, der die Interaktionen zwischen den Elementen verarbeitet
@callback(
    Output(component_id='histo-chart-final', component_property='figure'),
    Input(component_id='my-radio-buttons-final', component_property='value')
)
def update_graph(col_chosen):
    fig = px.histogram(df, x='continent', y=col_chosen, histfunc='avg')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)