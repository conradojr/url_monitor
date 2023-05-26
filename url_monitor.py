import requests
import time
import dash
import dash_core_components as dcc
import dash_html_components as html
import numpy as np
import pandas as pd

def read_urls(file_name):
    """Reads a file with some URLs."""
    with open(file_name, "r") as f:
        urls = f.readlines()
    return urls

def check_urls(urls):
    """Checks the URLs and gets the HTTP Code response."""
    response_data = []
    for url in urls:
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            continue
        response_data.append({
            "url": url,
            "http_code": response.status_code,
            "response_time": response.elapsed.total_seconds(),
        })

    return response_data

def main():
    """The main function."""
    file_name = "urls.txt"
    urls = read_urls(file_name)

    # Create a Dash app.
    app = dash.Dash(__name__)

    # Create a layout for the dashboard.
    layout = html.Div([
        html.H1("URL Monitor"),
        dcc.Graph(id="url-graph", figure=figure),
        dcc.Table(id="url-table", data=unique_line, style_cell_conditional=[
            {'if': {'column_name': 'url'}, 'width': '100px'},
            {'if': {'column_name': 'http_code'}, 'width': '200px'},
            {'if': {'column_name': 'response_time'}, 'width': '300px'},
        ]),
    ])

    # Update the dashboard every 60 seconds.
    @app.callback(
        Output("url-graph", "figure"),
        [Input("interval", "interval")],
    )
    def update_graph(interval):
        # Get the latest HTTP Code responses.
        response_data = check_urls(urls)

        # Create a figure for the dashboard.
        figure = px.line(response_data, x="response_time", y="http_code", color="url")

        # Create a unique line with all informations.
        unique_line = []
        for url in urls:
            unique_line.append({
                "url": url,
                "http_code": response_data[url]["http_code"],
                "response_time": response_data[url]["response_time"],
            })

        # Update the dashboard with the unique line.
        app.layout = html.Div([
            html.H1("URL Monitor"),
            dcc.Graph(id="url-graph", figure=figure),
            dcc.Table(id="url-table", data=unique_line),
        ])

        return figure

    # Run the app.
    app.run_server(debug=True)

if __name__ == "__main__":
    main()
