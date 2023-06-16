
This repository hosts an interactive visualization application that makes use of various datasets available on the [New York Open Data Portal](https://opendata.cityofnewyork.us/). Developed in Python, it leverages libraries such as Plotly, Dash, Pandas, and GeoPandas for data loading, preprocessing, and visualization.

The application provides a powerful and intuitive interface to explore a wealth of information on New York City in an interactive manner. It incorporates Polygon and MultiPolygon data in GeoJSON format for geographical visualization. A key feature of this application is its use of interactive controls, allowing users to adjust visualization parameters on the fly for a more tailored analysis experience.

Our goal is to make complex data accessible and understandable to a broad audience, ultimately empowering users to explore and understand New York data like never before.

## Key Technologies
- **Python**: This is the primary programming language used for development.
- [**Plotly**](https://github.com/plotly/plotly.py): Plotly is employed for generating, styling and setup of the data visualizations.
- [**Dash**](https://github.com/plotly/dash): Dash is the main framework for building the backend of this web application. Besides serving as a backend, Dash is also used for creating interactive, web-based dashboards with Plotly visualizations. It bridges the gap between front-end updates and back-end responses, hence allowing user interactions with the visualizations.
- **Pandas and GeoPandas**: These libraries are used for loading and preprocessing the datasets before visualizations. GeoPandas extends the datatypes used by pandas to allow spatial operations on geometric types, making it a convenient tool for geographical data manipulation.
- **GeoJSON**: GeoJSON files containing Polygon and MultiPolygon data are used to accurately visualize geographical boundaries and regions.

## Features
This application offers a wide array of interactive visualization features, making it a powerful tool for data exploration:

1. **Interactive Map**: Central to the application is an interactive map layered with various datasets. The map is controllable by multiple controls that enable users to filter and choose specific data points for display and exploration.

    - **Category Selector**: A drop-down menu that allows users to narrow down the available datasets to a specific category. This makes it easier to find and work with data from a particular domain of interest.

    - **Filter Selector**: Once a category is selected, users can then utilize the filter selector to choose specific datasets from that category. With close to 40 different datasets available, this feature helps users drill down to the exact data they need.

    - **Data Visualization**: The datasets are visualized in three formats:

        - **Points**: These are visual representations of individual data points from the datasets. Each point corresponds to a unique record or event in the data.

        - **Layers**: This involves placing polygon/multipolygon data onto the map, allowing for visualization of geographical boundaries, regions, or zones. Each layer can represent a different data variable, making it possible to visualize multiple variables simultaneously.

        - **Choropleth**: A choropleth map uses different color intensities or patterns within defined geographical areas to represent the values of a particular variable in the data. This provides an easy way to visualize how a measurement varies across a geographic area.

    - All points on the dashboard are clickable, showing additional information for the selected data point. This interactive feature allows users to get more detailed insights on demand.

2. **Data Details Drawer**: A click on the 'Data Details' button opens a drawer that shows detailed information about every selected dataset. This includes a description, the date the dataset was published, and a link to the source of the dataset.

3. **Time-Series Multi-Line Chart**: This chart displays long-term data trends for various indicators. Users can select a specific year for a more drilled-down view of the data, showing trends at a monthly level for that year.

4. **Demographics Stacked Bar Chart**: This chart visualizes demographic data of New York City boroughs. It allows users to understand the population composition of different areas at a glance.

5. **Indicator Radar Chart**: This complex chart shows various indicators (Poverty, Unemployment, Air Pollution, Bike Coverage, Smoking, Obesity) for each borough of New York City. It provides a comprehensive overview of the socio-economic and environmental status of the boroughs.

6. **Year Selector Slider**: Both the Demographics Stacked Bar Chart and the Indicator Radar Chart are equipped with a slider for selecting a specific year. This allows users to easily view changes over time in the demographic makeup and various indicators for the boroughs.

These features are designed to give users the flexibility and control to explore data in ways that best suit their needs. They make data exploration more intuitive and engaging, and also allow users to uncover insights that might otherwise remain hidden.

## Getting Started

### Prerequisites
The following software is needed to be installed on the local machine:
- Python (tested with version 3.10.X): 
    - You can check if python is already installed in the Terminal with the following command: `python --version`
    - Direct Link to Windows Setup 64-bit: [Python 3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
    - Direct Link to macOS Setup: [Python 3.10.11](https://www.python.org/ftp/python/3.10.11/python-3.10.11-macos11.pkg)
- All commands shown in the setup section expect that the Terminal is in the main folder of the application
### Setup
1. Start a terminal and switch into the mail folder of the application, e.g. `cd nyc-data-dashboard`
2. Create a new virtual environment: `python -m venv .venv`
3. Switch into the virtual environment
   - Windows: `.venv/Scripts/activate`
   - Linux/macOS: `source .venv/bin/activate`
   - The terminal should indicate that it has been switched into the virtual environment by showing it at the left side of the command line, e.g. `(.venv)`
4. Install the dependecies by executing `pip install -r requirements.dev.txt`
   - Alternatively if anaconda is used: `conda install -r requirements.dev.txt` 
   - The installation of the packages could take a few minutes  

### Starting the application
1. Ensure the virtual environment is active (There should be e.g. `(.venv)` shown at the left side)
2. Start the application by executing `python app.py` 
3. After loading the application the terminal should show that is has successfully started and is serving the application e.g. on `http://127.0.0.1:8050/`

Example output:
```bash
(.venv) PS C:\Users\oleba\Documents\git\nyc-data-dashboard> python app.py
-------------------------------------------
App initialized
Loading and preprocessing data...
Data loading time: 00:00:05 seconds
Successfully loaded 39 datasets
Starting NYC Smart City Dashboard app
Starting Dash server
Dash is running on http://127.0.0.1:8050/

 * Serving Flask app 'app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:8050
Press CTRL+C to quit
```

## Used third-party libraries
#### Main components
- plotly
- dash
- flask
- dash-core-components
- dash-bootstrap-components
- dash-mantine-components

#### Data handling
- pandas
- scipy
- numpy
- openpyxl

#### Geodata processing
- shapely
- geopandas