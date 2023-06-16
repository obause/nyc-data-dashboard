"""
    Callbacks for the interaction between the different components of the dashboard
    and the data visualizations as well as the interaction from one component to another.
"""

from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash_iconify import DashIconify

import numpy as np
import pandas as pd

import plotly.express as px
import plotly.graph_objects as go

import data_preprocessing


def get_callbacks(app, mapbox_access_token, data_dict, filter_options, attributes):
    """Returns the callbacks for the different components of the dashboard.

    Args:
        app (dash.Dash): The dash application object handler.
        mapbox_access_token (str): The mapbox access token.
        data_dict (dict): A json structured object where all metadata and data is stored. 
        filter_options (dict): All filter options available for the map including some metadata.
        attributes (dict): All attributes available for the table.
    """
    
    # Generate Filter Options based on category selected and active filters
    @app.callback(
        Output('map-filter', 'children'),
        Input('map-category', 'value'),
        State('map-filter', 'value'))
    def set_filter_options(selected_category, selected_filters):
        """This callback generates the filter options based on the selected category and the active filters.

        Args:
            selected_category (str): The value of the category dropdown element.
            selected_filters (list): The list of selected filters.

        Returns:
            list: All filter options for the selected category.
        """
        app.logger.debug("Selected category: ", selected_category)
        
        options = []
        if selected_category is None:
            return options
        else:
            if selected_filters is not None:
                for i in selected_filters:
                    options.append(
                        dmc.Chip([
                            DashIconify(
                                    icon=filter_options[i].get('icon', 'fa:circle'),
                                    width=17,
                                    height=17,
                                    inline=True,
                                    style={"marginRight": 5},
                                    #color=icon_color,
                                    ),
                            filter_options[i]['name']
                        ], value=i, variant="outline")
                    )
            for key, value in filter_options.items():
                #icon_color = data_dict[key].get('color', 'black') if data_dict[key].get('type') == 'points' else 'black'
                if selected_category == value['category']:
                    options.append(
                        dmc.Chip([
                            DashIconify(
                                icon=value.get('icon', 'fa:circle'),
                                width=17,
                                height=17,
                                inline=True,
                                style={"marginRight": 5},
                                #color=icon_color,
                                ),
                            value['name'], 
                            ],
                            value=key, 
                            variant="outline"
                            )
                        )
        return options

    # Update Map based on selected filters and their visualization type
    @app.callback(
        Output('map', 'figure'),
        Input('map-filter', 'value'))
    def update_map(filter_values):
        """Updates the map based on the selected filters and their visualization type.

        Args:
            filter_values (list): List of selected filters.

        Returns:
            figure: Map figure.
        """
        app.logger.debug("Selected Filters: {}".format(filter_values))
        
        layers = []
        center = { 'lon': -73.935242, 'lat': 40.730610}
        zoom = 10
        
        fig_map = go.Figure(go.Scattermapbox())
        
        if filter_values is not None:
            for filter_value in filter_values:
                if filter_options[filter_value].get('connected_to') is not None:
                    filter_values.append(filter_options[filter_value]['connected_to'])
                    app.logger.debug("{} connected to: {}".format(filter_value, filter_options[filter_value]['connected_to']))
                
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
                    app.logger.debug("is points")
                    data = data_dict[filter_value]['data']
                    fig_map.add_trace(go.Scattermapbox(
                        lon = data.Longitude, lat = data.Latitude,
                        marker = data_dict[filter_value].get('marker_style'),
                        text=data_dict[filter_value].get('text'),
                        mode=data_dict[filter_value].get('mode', 'markers'),
                        name=data_dict[filter_value].get('name'),
                    ))
                    
                elif filter_options[filter_value]['type'] == 'density':
                    app.logger.debug("is density")
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
                    app.logger.debug("is chloropeth")
                    geodata = data_dict[filter_value]['geodata']
                    data = data_dict[filter_value]['data']
                    values = data_dict[filter_value].get('values')

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


    # Display data of selected point in map
    @app.callback(
        Output('map-click-data', 'children'),
        Input('map', 'clickData'),
        State('map-filter', 'value')
        )
    def display_click_data(clickData, state):
        """Displays the data of the selected point in the map.

        Args:
            clickData (dict): A dictionary containing information about the clicked point.
            state (list): A list of selected filters.

        Returns:
            str: A html table containing the data of the selected point. 
        """
        #print("clickData: ", clickData)
        #print("state: ", state)
        
        if clickData is None:
            return "Click on a point to see its data"
        
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
        
        header = [html.Thead(html.Tr([html.Th("Attribute"), html.Th("Value")]))]
        rows = [html.Tr([html.Td(attributes_list[col]), html.Td(str(value).replace("True", "Yes"))]) for col, value in point_data.items() if col in selected_attributes]
        table = [html.Thead(header), html.Tbody(rows)]
        return table #json.dumps(clickData, indent=2)

    # Update the line chart based on dropdown selection
    @app.callback(
        Output("graph", "figure"),
        Input("dropdown", "value")
    )
    def update_line_chart(selected_year):
        """Updates the line chart based on the selected year.

        Returns:
            figure: The line chart.
        """
        df = data_preprocessing.get_timeline()
        
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
        )  
        return fig

    # Update the bar chart based on slider selection
    @app.callback(
        Output("stacked", "figure"),
        Input("slider", "value")
    )
    def update_stacked(selected_year):
        """Updates the bar chart based on the selected year.

        Args:
            selected_year (int): The selected year.

        Returns:
            figure: The bar chart.
        """
        df_stacked_2022, df_stacked_2018, df_stacked_2015 = data_preprocessing.get_measures_stacked()
        
        if selected_year == 3:
            fig = px.bar(data_frame= df_stacked_2022, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                        title="Distribution of Age")
        elif selected_year == 2:
            fig = px.bar(data_frame= df_stacked_2018, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                        title="Distribution of Age")
        else:
            fig = px.bar(data_frame= df_stacked_2015, x="Borough", y="Percent", color="Range",opacity=0.9,orientation="v",barmode="relative",
                        title="Distribution of Age")
        
        fig.update_layout(
            title_x=0.5,
        )
        return fig

    # Update the radar chart based on slider selection
    @app.callback(
        Output("radar", "figure"),
        Input("slider", "value")
    )
    def update_radar(selected_year):
        """Updates the radar chart based on the selected year.

        Args:
            selected_year (int): THe selected year.

        Returns:
            figure: The radar chart.
        """
        df_stacked_2022, df_stacked_2018, df_stacked_2015 = data_preprocessing.get_measures_stacked()
        
        if selected_year == 3:
            fig = px.line_polar(df_stacked_2022, r="Percent", 
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
            fig = px.line_polar(df_stacked_2018, r="Percent", 
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
            fig = px.line_polar(df_stacked_2015, r="Percent", 
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
        fig.update_yaxes(range=[1000, 4000])
        fig.update_layout(
            title_x=0.5,
            yaxis_range=[1000,4000]
        )
        return fig

    dropdown_options_cd = [{"label": f"{value['GEONAME']} ({value['GEOCODE']})", "value": value['GEOCODE']} for i, value in data_preprocessing.get_community_districts_geodf().iterrows()]

    # Generate drawer content based on selected datasets
    @app.callback(
        Output("drawer-data-details", "children"),
        Input("map-filter", "value"),
        #prevent_initial_call=True,
    )
    def drawer_data_details(filter_values):
        """Generates the drawer content based on the selected datasets.

        Args:
            filter_values (list): The selected datasets.
        
        Returns:
            list: A list of html components.
        """
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
                    dmc.Text("Source:"),
                    html.A(filter_options[filter_value].get('source'), href=filter_options[filter_value].get('source')),
                    dmc.Divider(variant="solid"),
                ]
        return content

    # Open drawer when button is clicked
    @app.callback(
        Output("drawer-data-details", "opened"),
        Input("data-details-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def open_drawer(n_clicks):
        """Opens the drawer when the button is clicked.

        Returns:
            bool: True if the drawer is opened, False otherwise.
        """
        return True

    @app.callback(
    Output('cd-demographics', 'style'),
    Input('cd-dropdown', 'value'))
    def hide_cd_demo(cd):
        """Hides the cd demographics graph if no cd is selected.

        Args:
            cd (str): The community district number.

        Returns:
            dict: A dictionary containing the style of the graph.
        """
        if cd is None:
            return {'display': 'none'}

    @app.callback(
        Output('cd-demographics', 'figure'),
        Input('cd-dropdown', 'value'))
    def update_cd_demo(cd):
        if cd is None:
            cd = 201
        print("selected cd: ", cd)
        #filtered_df = demo_ages_cd[demo_ages_cd["cd_number"] == cd]
        filtered_df = pd.DataFrame()
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
            labels=data_preprocessing.get_cd_demographic_legend()
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
            title='Population by Age and Gender'
        )
        fig.update_traces(width=0.4)
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
            # center = community_districts_geodf[community_districts_geodf['GEOCODE']==selected_cd][['Latitude', 'Longitude']].values[0].tolist()
            center = pd.DataFrame()
            community_districts_geodf = pd.DataFrame()
            community_districts_geo = pd.DataFrame()
            zoom = 12
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
        cd_indicators = pd.DataFrame()
        if selected_cd is None:
            selected_cd = 201
        print("selected cd: ", selected_cd)
        filtered_df = cd_indicators[cd_indicators["cd_number"] == selected_cd]

        fig = go.Figure()

        fig.add_trace(go.Indicator(
            title = {"text": "Foreign-Born Population<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>% of residents are foreign-born</span>"},
            mode = "number",
            number = {'suffix': "%"},
            value = filtered_df['pct_foreign_born'].values[0],
            domain = {'row': 0, 'column': 0}))

        fig.add_trace(go.Indicator(
            title = {"text": "Unemployment<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>% of unemployed residents</span>"},
            mode = "number",
            number = {'suffix': "%"},
            value = filtered_df['unemployment'].values[0],
            domain = {'row': 0, 'column': 1}))

        fig.add_trace(go.Indicator(
            title = {"text": "Commute to Work<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>mean in minutes</span>"},
            mode = "number",
            number = {'suffix': "min"},
            value = filtered_df['mean_commute'].values[0],
            domain = {'row': 3, 'column': 0}))

        fig.add_trace(go.Indicator(
            title = {"text": "English Proficiency<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>% having limited English proficiency</span>"},
            mode = "number",
            number = {'suffix': "%"},
            value = filtered_df['lep_rate'].values[0],
            domain = {'row': 3, 'column': 1}))

        fig.add_trace(go.Indicator(
            title = {"text": "Poverty Measure<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>% of incomes below poverty threshold</span>"},
            mode = "number",
            number = {'suffix': "%"},
            value = filtered_df['poverty_rate'].values[0],
            domain = {'row': 6, 'column': 0}))

        fig.add_trace(go.Indicator(
            title = {"text": "Rent Burden<br><span style='font-size:0.6em;color:gray;line-height: 0.8;'>% of households spend 35%<br>or more of their income on rent</span>"},
            mode = "number",
            number = {'suffix': "%"},
            value = filtered_df['pct_hh_rent_burd'].values[0],
            domain = {'row': 6, 'column': 1}))

        fig.update_layout(
            grid = {'rows': 7, 'columns': 2, 'pattern': "independent"},
            template = {'data' : {'indicator': [{
                'title': {'text': "Speed"},
                'mode' : "number+delta+gauge",
                'delta' : {'reference': 90}}]
                                }},    
            )
        return fig