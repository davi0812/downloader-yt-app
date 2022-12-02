import dash
from youtube_dl import YoutubeDL
from flask import request
from dash.dependencies import Input, Output, State
import json

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
from process import *

app = dash.Dash(__name__, external_stylesheets=external_stylesheets, use_pages=True)
server = app.server
# intial layout
app.layout = html.Div([
    # html.Div(
    #     [
    #         dcc.Link(
    #             f"{page['name']} - {page['path']}", href=page["relative_path"],
    #             style={"margin": "0px 20px"}
    #         )
    #         for page in dash.page_registry.values()
    #     ]
    # ),
    dash.page_container
])


# layout after an upload is detected
def parse_contents(link):
    if link is not None:
        audio = ""
        extension = ""
        grupos = []

        with YoutubeDL({'outtmpl': 'assets/%(id)s.%(ext)s', 'format': 'bestaudio'}) as ydl:
            info = ydl.extract_info(link, download=True)
            extension = info["ext"]
            id = info["id"]
            audio = "assets/" + id + "." + extension
            if check(id) == 0:
                file_ready = convert_to_wav(id, audio, extension)
                do_diarization(file_ready)
                grupos = do_grouping()
                gidx, speakers, timestamps = do_split(id, grupos)
                nuevodiv = do_transcribe(id, gidx, speakers, timestamps)
                transfer(id)
            else:
                return html.Div(children=[
                    html.P("It has already been processed"),
                    dcc.Link("Visit "+id, href="http://159.223.207.111/downloader/list.php?id="+id)
                ])
        return html.Div([
            html.H5(link),
            html.Audio(id="player", autoPlay=True, src=audio, controls=True, style={"width": "50%"}),
            html.Hr(),
            html.Div('Transcript'),
            html.Plaintext(audio),
            nuevodiv
        ])


def changeNames(link, hijos):
    childs = hijos
    id = ""
    with YoutubeDL({'outtmpl': 'assets/%(id)s.%(ext)s', 'format': 'bestaudio'}) as ydl:
        info = ydl.extract_info(link, download=False)
        extension = info["ext"]
        id = info["id"]
    finales = len(childs["props"]["children"][5]["props"]["children"])
    inputs = childs["props"]["children"][5]["props"]["children"][finales - 1]["props"]["children"]
    for valor in inputs:
        speak = valor["props"]["id"]
        newSpe = valor["props"]["value"]
        update_db(id, speak, newSpe)
    return html.Div([
        html.Meta(httpEquiv="refresh", content="3"),
        html.H5("Values Updated")
    ])


@app.callback(Output('output_div', 'children'),
              [Input('submit-button', 'n_clicks')],
              [Input('changes', 'n_clicks')],
              [State('link', 'value')],
              [State('output_div', 'children')],
              )
def update_output(clicks, changes, input_value, hijos):
    if changes is not None and hijos is not None:
        return changeNames(input_value, hijos)

    if clicks is not None and hijos is None:
        return parse_contents(input_value)


if __name__ == '__main__':
    app.run(debug=True, dev_tools_hot_reload=False)
