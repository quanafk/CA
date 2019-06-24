import os
import dash
from dash import Dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
# from app import app
import plotly.graph_objs as go
# import colorlover as cl
import pandas as pd
import numpy as np
import base64

available_dropphase = ['Water', 'L151']
available_substrate = ['PCM PFA','PCM FEP','PCM KYNAR','PCM SPO','PCM ECTFE','HDPE']
available_ambient = ['Air', 'L151', 'L453']

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server
# app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Dynamic Contact Angle Analysis'),

    html.Div(children='''
        Created by Quan Xie (quan.xie@liquiglide.com), Copyright 2019
    '''),

    html.Div([
        html.Div([
            html.Div([
                html.Label('Substrate'),
                dcc.Dropdown(
                    id='Substrate',
                    options=[{'label': i, 'value': i} for i in available_substrate],
                    style={'height': '30px', 'width': '300px'},
                    value='PCM PFA'
                )
            ], style={'padding': 20}),

            html.Div([
                html.Label('Droplet'),
                dcc.Dropdown(
                    id='Droplet',
                    options=[{'label': i, 'value': i} for i in available_dropphase],
                    style={'height': '30px', 'width': '300px'},
                    value='Water'
                )
            ], style={'padding': 20}),

            html.Div([
                html.Label('Ambient'),
                dcc.Dropdown(
                    id='Ambient',
                    options=[{'label': i, 'value': i} for i in available_ambient],
                    style={'height': '30px', 'width': '300px'},
                    value='L151'
                )
            ], style={'padding': 20}),
        ]),

        html.Div([
            html.Img(id='CA-image',
                style={'height': '75%', 'width': '75%'})
        ], style={'textAlign': 'center'})
    ],style = {'columnCount': 2}),

    dcc.Graph(id='CA-graph'),


])

@app.callback(
    Output('CA-graph', 'figure'),
    [Input('Droplet', 'value'), Input('Substrate', 'value'), Input('Ambient', 'value')])
def update_figure(selected_droplet, selected_substrate, selected_ambient):
    Droplet_Phase = selected_droplet
    Substrate = selected_substrate
    Ambient_Phase = selected_ambient
    folder_path = "/Users/qxie/Dropbox (LiquiGlide Inc.)/RameHart Goniometer Data/Cosmetic Transfer Tank Project/Data Analysis/"
    file_name = "Dynamic - "+Droplet_Phase+"-"+Substrate+"-("+Ambient_Phase+").xlsx"
    file_path = folder_path + file_name

    image_folder = "/Users/qxie/Dropbox (LiquiGlide Inc.)/RameHart Goniometer Data/Cosmetic Transfer Tank Project/Raw Data/"
    image_file = Droplet_Phase+"-"+Substrate+"-("+Ambient_Phase+")"
    image_path = image_folder + image_file + ".BMP"

    df = pd.read_excel(file_path)
    df.columns = ['No.', 'Time', 'ThetaL', 'ThetaR', 'Mean', 'Dev.', 'Height', 'Width', 'Area', 'Volume', 'Messages']



    dfl = df.loc[((df.ThetaL > 0) & (df.ThetaL < 180) & (df.Messages != '   Error in profile dat')), ['Time', 'ThetaL', 'Messages']]
    dflx = df.loc[((df.ThetaL <= 0) | (df.ThetaL >= 180) | (df.Messages != '   Error in profile dat')), ['Time', 'ThetaL', 'Messages']]
    dfr = df.loc[((df.ThetaR > 0) & (df.ThetaR < 180) & (df.Messages != '   Error in profile dat')), ['Time', 'ThetaR', 'Messages']]
    dfrx = df.loc[((df.ThetaR <= 0) | (df.ThetaR >= 180) | (df.Messages != '   Error in profile dat')), ['Time', 'ThetaR', 'Messages']]
    dfw = df[['Time', 'Width']]
    traceW = go.Scatter(
        x = dfw.Time,
        y = dfw.Width,
        mode = 'lines',
        name = 'Width ' + image_file,
        yaxis = 'y2',
    )
    traceL = go.Scatter(
        x = dfl.Time,
        y = dfl.ThetaL,
        mode = 'lines',
        name = 'ThetaL ' + image_file
    )
    traceR = go.Scatter(
        x = dfr.Time,
        y = dfr.ThetaR,
        mode = 'lines',
        name = 'ThetaR ' + image_file
    )
    traces = [traceW, traceL, traceR]

    layout = go.Layout(
        title = image_file,
        yaxis = dict(
            title = 'Contact Angle (deg)'
        ),
        yaxis2 = dict(
            title = 'Width (mm)',
            titlefont = dict(
                color='#1f77b4'
            ),
            tickfont = dict(
                color='#1f77b4'
            ),
            # range = [0,4],
            overlaying = 'y',
            side = 'right'
        ),
        xaxis = dict(
            title = 'Time (seconds)',
            # rangeselector = dict(
            #     buttons = list([
            #         dict(count = 20,
            #              label = '1s',
            #              step = 'second',
            #              stepmode = 'backward'),
            #         dict(count = 5,
            #              label = '5s',
            #              step = 'second',
            #              stepmode = 'backward'),
            #         dict(label = 'ALL',
            #             step = 'all',
            #             visible = True),
            #     ])
            # ),
            # rangeslider = dict(
            #     visible = True
            # ),
            # type = 'date'
        )
    )

    fig = go.Figure(data=traces, layout=layout)
    return fig

@app.callback(
    dash.dependencies.Output('CA-image', 'src'),
    [Input('Droplet', 'value'), Input('Substrate', 'value'), Input('Ambient', 'value')])
def update_image_src(selected_droplet, selected_substrate, selected_ambient):
    Droplet_Phase = selected_droplet
    Substrate = selected_substrate
    Ambient_Phase = selected_ambient
#     image_folder = "/Users/qxie/Dropbox (LiquiGlide Inc.)/RameHart Goniometer Data/Cosmetic Transfer Tank Project/Raw Data/"
    image_file = Droplet_Phase+"-"+Substrate+"-("+Ambient_Phase+")"
    image_path = image_folder + image_file + ".BMP"
    encoded_image = base64.b64encode(open(image_path, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())



if __name__ == '__main__':
    app.run_server()
