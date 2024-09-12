# Import required libraries
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("./spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)


def label(x):
    if x == 0:
        return "Fail"
    else:
        return "Success"


# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options=[{'label': i, 'value': i} for i in
                                                      spacex_df['Launch Site'].unique()],
                                             value='ALL',
                                             clearable=False),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=min_payload,
                                                max=max_payload,
                                                value=[min_payload, max_payload],
                                                marks={i: str(i) for i in
                                                       range(int(min_payload), int(max_payload) + 1, 1000)},
                                                step=100),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])


# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        all_df = spacex_df[spacex_df['class'] == 1]
        all_df = all_df['Launch Site'].value_counts().reset_index().rename(columns={"index": "unique_values", 0: "counts"})
        fig = px.pie(all_df,values=all_df['count'], names='Launch Site', title='Total Successful Launches by Site')
        fig.update_traces(textinfo='value')
    else:
        df = spacex_df[spacex_df['Launch Site'] == selected_site]
        df['Status'] = df['class'].apply(label)
        df = df['Status'].value_counts().reset_index().rename(columns={"index": "unique_values", 0: "counts"})
        fig = px.pie(df, values=df['count'],names=df['Status'] , title=f'Success vs. Failed Counts for {selected_site}')
    return fig


@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):

    filtered_df = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) & (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if selected_site != 'ALL':

        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version',
                     title='Correlation between Payload and Launch Success')
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server()
