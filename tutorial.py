import json
import pandas as pd
import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

import dash  # (version 1.12.0) pip install dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

df = pd.read_csv("/Users/kevinmcdonough/Documents/Flatiron/phase_3/blog/dash_youtube/Dash-by-Plotly/Other/Dash_Introduction/clean_df.csv", index_col=0)

colors = {
    'background': '#111111',
    'text': '#C5DB5F'
}

app = dash.Dash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[

    html.H1("UFO Sightings in the U.S.", style={'text-align': 'center', 'color': colors['text']}),
    
    html.Div([
        html.Div([
            dcc.Dropdown(id="slct_decade",
                        options=[
                            {"label": "1940-1950", "value": "1940-1950"},
                            {"label": "1950-1960", "value": "1950-1960"},
                            {"label": "1960-1970", "value": "1960-1970"},
                            {"label": "1970-1980", "value": "1970-1980"},
                            {"label": "1990-2000", "value": "1990-2000"},
                            {"label": "2000-2010", "value": "2000-2010"},
                            {"label": "2010-2014", "value": "2010-2014"}],
                        multi=False,
                        value="2010-2014", 
                        style={'width': "50%"}
                        ),

            html.Div(id='output_container', style={'color': colors['text']}, children=[]),
            html.Br(),
        ], style={'width': '48%', 'display': 'inline-block'}),
        
        html.Div([
            dcc.Dropdown(id="slct_chart",
                        options=[
                            {"label": "Average Encounter (seconds)", "value": "avg_encounter"},
                            {"label": "UFO Sightings", "value": "sighting"}],
                        multi=False,
                        value="sighting",
                        style={'width': "76"}
                        ),
            html.Br(),
        ], style={'width': '49%', 'text-align': 'center', 'display': 'inline-block'})
    ], style={
        'padding': '10px 5px'
    }),
    html.Div([
        dcc.Graph(id='my_ufo_map',
        hoverData={'points': [{'customdata': ['TX', 0]}]}
        )
    ], style={'width': '49%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='my_bar_chart'),
    ], style={'display': 'inline-block', 'width': '49%'}),
    html.Div(id='my-hoverdata', style={'color': colors['text']})
])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components
@app.callback(
    [Output(component_id='output_container', component_property='children'),
     Output(component_id='my_ufo_map', component_property='figure')],
    [Input(component_id='slct_decade', component_property='value')]
)
def update_map(slct_decade):

    container = "The decade chosen by user was: {}".format(slct_decade)
    
    dff = df.copy()
    dff = dff.groupby(['decade', 'state']).count()[['sighting']]
    dff.reset_index(inplace=True)
    dff = dff[dff["decade"] == slct_decade]

    # Plotly Express
    fig = px.choropleth(
        data_frame=dff,
        locationmode='USA-states',
        locations='state',
        scope="usa",
        color='sighting',
        hover_data=['state', 'sighting'],
        color_continuous_scale=px.colors.sequential.Blugrn,
        labels={'sighting': 'UFO sightings'},
        template='plotly_dark'
    )

    return container, fig
    
def create_chart(df_new, slct_chart, hoverData):

    df_new = df_new.groupby('decade').sum()
    df_new.reset_index(inplace=True)
    df_new['avg_encounter'] = df_new['duration (seconds)'] / df_new['sighting']
    x = df_new['decade']

    fig = px.bar(df_new, x='decade', y=slct_chart, title=hoverData['points'][0]['customdata'][0], template='plotly_dark')

    fig.update_layout(title={'xanchor':'center', 'yanchor': 'top', 'y':0.9,'x':0.5,})

    return fig 

@app.callback(
    Output(component_id='my_bar_chart', component_property='figure'),
    [Input(component_id='my_ufo_map', component_property='hoverData'),
    Input(component_id='slct_chart', component_property='value')]
)

def update_chart(hoverData, slct_chart):
    state_name = hoverData['points'][0]['customdata'][0]
    df_new = df.copy()
    df_new = df_new[df_new['state'] == state_name]
    print(state_name)
    return create_chart(df_new, slct_chart, hoverData)

@app.callback(
Output('my-hoverdata', 'children'),
[Input('my_ufo_map', 'hoverData')])

def callback_image(hoverData):
    return json.dumps(hoverData, indent=2)


# ------------------------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)
