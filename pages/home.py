import dash
from dash import html, dcc
from youtube_dl import YoutubeDL
from dash.dependencies import Input, Output, State

dash.register_page(__name__, path='/')

layout = html.Div(children=[
    dcc.Input(
        placeholder='Ingrese la url del video...',
        type='text',
        value='',
        id='link',
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    ),
    html.Button(id='submit-button', type='submit', children='Submit'),
    html.Div(id='output_div'),
    html.Button(id='changes', children='Change Speaker'),
])
