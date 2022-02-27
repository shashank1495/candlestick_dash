import pandas as pd
import numpy as np
import yfinance as yf
import dash
import plotly.express as px
from dash.dependencies import Output, Input, State
import dash_core_components as dcc
import dash_html_components as html
from dash import dash_table
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
  
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LITERA]) 
server = app.server

app.layout = dbc.Container([
    
html.Div(children=[ 
    dbc.Row([
        dbc.Col([html.Div([html.H1(children='Stock Market Dashboard',className="mb-4")],className="mb-4")])
        ]),
    dbc.Row([
        dbc.Col([
            dbc.Row([ 
                dbc.Card([
                    html.Div(["Input Stock Symbol"],className="mb-4"),
                    html.Div([dbc.Input(id = "symbol", value = "^GSPC",type = "text")],className="mb-4"),
                    html.Div(["Select Date Range"],className="mb-4"),
                    html.Div([dcc.DatePickerRange(id = "date", start_date = "2021-01-01", end_date = "2021-02-02")],className="mb-4"),
                    html.Div(id = "range_slider_message",className="mb-4"),
                    html.Div([dcc.Dropdown(id= "graph_option",
                                           options = [{'label': 'Yes', 'value': 1},
                                                       {'label': 'No', 'value': 0}],                                                       
                                           value = 1,className="mb-4",style = {'display':'block'})]),
                    html.Div([dbc.Button(id="submit",n_clicks=0, children='Submit',color="primary")],className="mb-4")
                    ],body=True)
                ]),
            ],width = 3),
        dbc.Col([
            dbc.Row([
                dcc.Tabs(id = "tab", 
                         value = "Data",
                    children = [
                    dcc.Tab(
                        label = "Data",
                        value = "Data",
                        children = [dash_table.DataTable(id = "table")]
                        ,className="mb-4"),
                    dcc.Tab(
                        label = "Graphs",
                        value = "Graphs",
                        children = [
                            dbc.Card(dcc.Graph(id="plot",className="mb-4"),body = True)
                            ],className="mb-4"
                        )
                ])
                ]) 
            ],width = 9)
        ]),
],className="mb-4")
],fluid = True)

@app.callback( 
    Output('range_slider_message', 'children'),
    Output('graph_option', 'style'),
    Input('tab','value')
)
      
def update_dropdown(tab):
    if tab=="Data":
        return  [" "], {'display':'none'}
    else:
        return  ["Turn on Range Slider"], {'display':'block'}
        
@app.callback( 
    Output('table', 'data'),
    Output('table', 'columns'),
    Input('submit','n_clicks'),
    State('symbol', 'value') ,
    State('date', 'start_date'),
    State('date', 'end_date')
)
def update_table(n_clicks,symbol,start_date,end_date):
    data = n_clicks
    data = yf.Ticker(symbol).history(start = start_date,end = end_date,interval = "1d")
    data = data.reset_index()
    data.loc[:,"Date"] = pd.to_datetime(data.loc[:,"Date"],"%Y-%m-%d %H-%M-%S").dt.date
    data = data.loc[:,["Date","Open","High","Low","Close"]]
    
    col = pd.DataFrame() 
    col.loc[:,"id"] = list(data.columns)
    col.loc[:,"name"] = list(data.columns)
    
    return data.to_dict("records"), col.to_dict("records")

@app.callback( 
    Output('plot', 'figure'),
    Input('submit','n_clicks'),
    State('symbol', 'value') ,
    State('date', 'start_date'),
    State('date', 'end_date'),
    State("graph_option", "value") 
)
  
def update_fig(n_clicks,symbol,start_date,end_date,graph_option):
    data = yf.Ticker(symbol).history(start = start_date,end = end_date,interval = "1d")
    data = data.reset_index()
    data.loc[:,"Date"] = pd.to_datetime(data.loc[:,"Date"],"%Y-%m-%d %H-%M-%S").dt.date
    data = data.loc[:,["Date","Open","High","Low","Close"]]
    
    # fig = px.line(data,x="Date",y="Close") 
    fig = go.Figure(data = [go.Candlestick(x = data["Date"],
                                          open = data["Open"],
                                          high = data["High"],
                                          low = data["Low"],
                                          close = data["Close"]
                                          )])    
    fig.update_layout(
        title = (symbol+" Candlestick chart"),
        yaxis_title = "Share Price",
        height = 800,
        paper_bgcolor = "#ffffff",
        plot_bgcolor = "#ffffff",
        xaxis = dict(color = "#000000", linecolor = "#000000", nticks = 10, gridcolor = "#ffffff",
                     rangeselector = dict(bgcolor = "#e5e5e5")
                     ),
        yaxis = dict(color = "#000000", linecolor = "#000000", gridcolor = "#ffffff"),
        xaxis_rangeslider_visible=(graph_option==1))
    fig.add_trace(go.Scatter(x=data["Date"],y=data["Close"]))
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
