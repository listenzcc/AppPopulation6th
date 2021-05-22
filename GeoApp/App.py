'''
File: App.py
Author: Chuncheng
Version: 0.0
Purpose: Establish Web App using Dash
'''

# Imports
import traceback

import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from .DataManager import DataManager
from . import PackageInfo, ProvinceMap, logger

# ---- Settings ----
# Init DataManager
dm = DataManager()


class DynamicData(object):
    ''' The Dynamic Data Container'''

    def __init__(self):
        ''' Initialize with uniques as options1 '''
        uniques = dm.get_uniques()
        options1 = [{'label': e, 'value': j} for j, e in enumerate(uniques)]
        self.options1 = options1
        logger.info('Initialized Dynamic Data Container')

    def update_fig(self, idx=1):
        ''' Make fig for the column idx of [idx].

        Args:
        - @idx: The column idx being selected, default value is 1.
        '''
        col = self.body.columns[idx]
        logger.info(f'Building Fig for "{self.title} - {col}".')
        self.body = self.body.astype({col: 'float'})

        if 'Location' not in self.body.columns:
            logger.error(
                f'Failed update_fig since "location" is not in the columns.')
            return
        fig = px.choropleth_mapbox(
            data_frame=self.body,
            geojson=ProvinceMap,
            color=col,
            locations='Location',
            featureidkey="properties.NL_NAME_1",
            color_continuous_scale='viridis',
            title=f'{self.title} - {col}',
        )
        fig.update_layout(mapbox_style="light",
                          mapbox_accesstoken=PackageInfo['mapboxToken'],
                          mapbox_zoom=3,
                          mapbox_center={"lat": 37.110573, "lon": 106.493924})
        self.fig = fig
        fig.write_html('a.html')
        logger.info(f'Built Fig for "{self.title} - {col}".')

        pass

    def change_unique_idx(self, idx=0):
        ''' Select the index [idx] of the options1.

        Args:
        - @idx: The selected index , default by 0.
        '''
        try:
            unique = dm.get_path_by_unique(self.options1[idx]['label'])
            title, columns, body = dm.fetch_path(unique)
            options2 = [{'label': e, 'value': j}
                        for j, e in enumerate(columns)]
            self.options2 = options2
            self.title = title
            self.body = body

        except:
            err = traceback.format_exc()
            logger.error(f'Failed change_unique_idx, error is "{err}"')


dd = DynamicData()
dd.change_unique_idx(0)
dd.update_fig(1)

# Init App
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = PackageInfo['packageName']

# ---- Layout ----
# Logo Div
logo_div = html.Div([
    html.H2('Population Geo Dash'),
])

# Controller Div
control_div = html.Div([
    dcc.Dropdown(
        id='dropdown1',
        options=dd.options1,
        value=0
    ),
    dcc.Dropdown(
        id='dropdown2',
        options=dd.options2,
        value=0
    )
])

# Display Div
display_div = html.Div([
    dcc.Graph(id='graph1',
              figure=dd.fig,
              style={'height': '800px'}
              )
])

# Place
app.layout = html.Div([
    logo_div,
    control_div,
    html.Div(id='display-value'),
    display_div
])


@app.callback([Output('graph1', 'figure'),
               Output('dropdown2', 'options')],
              [Input('dropdown1', 'value'),
               Input('dropdown2', 'value')])
def display_value(value1, value2):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    logger.info(f'Changed ID is "{changed_id}".')

    if changed_id.startswith('dropdown1.'):
        dd.change_unique_idx(value1)

    if changed_id.startswith('dropdown2.'):
        dd.update_fig(value2)

    return dd.fig, dd.options2


def run_server():
    app.run_server(debug=True)
