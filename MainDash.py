import json
import plotly_express as px
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from WeatherSpider import *


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(id='graph'),
    dcc.Input(id='input_', type='text', value='北京'),
    html.Button(id='submit', n_clicks=0, children='Submit'),
    dcc.Interval(id='update', interval=86400000, n_intervals=0),
    html.Div(id='intermediate-value')
])


def select_province(df, name):
    return df.loc[df['省/直辖市'] == name]


def main(df, name):
    province = select_province(df, name)

    if name == '广西':
        name = '广西壮族自治区'
    elif name == '内蒙古':
        name = '内蒙古自治区'
    elif name == '宁夏':
        name = '宁夏回族自治区'
    elif name == '西藏':
        name = '西藏自治区'
    elif name == '新疆':
        name = '新疆维吾尔自治区'
    elif name == '上海':
        name = '上海市'
    elif name == '重庆':
        name = '重庆市'
    elif name == '北京':
        name = '北京市'
    elif name == '天津':
        name = '天津市'
    else:
        name += '省'

    with open(f"city/{name}.json", 'r', encoding='utf-8') as fp:
        geo = json.load(fp)

    city = []
    for c in geo['features']:
        d = {}
        d['name'] = c['properties']['name']
        d['adcode'] = c['properties']['adcode']
        city.append(d)

    city_code = pd.DataFrame(city)

    df = province.join(city_code.set_index('name'), on='城市')

    fig = px.choropleth(df, geojson=geo, locations='adcode',
                        featureidkey='properties.adcode', color='最高气温',
                        hover_data=['城市', '最高气温', '最低气温'], title=f'{name}')
    fig.update_geos(fitbounds="locations", visible=False)

    return fig


@app.callback(Output('intermediate-value','children'), [Input('update','n_intervals')])
def update_data(n):
    weather.job()
    weather.send_message('济南', weather.city_list)

    return "更新时间：{}".format(time.strftime("%Y-%m-%d %H:%M:%S",
                                              time.localtime(weather.last_time)))


@app.callback(Output('graph', 'figure'),
              [Input('submit', 'n_clicks')],
              [State('input_', 'value')])
def update_output(n_clicks, input_):
    time.sleep(2)
    df = pd.DataFrame(weather.city_list)
    df['城市'] = df['城市'].map(lambda x: x + '市')
    index = df.query("`省/直辖市` in ['北京','上海','天津','重庆']")['城市'].index
    df.loc[index,'城市'] = df.query("`省/直辖市` in ['北京','上海','天津','重庆']")['城市'].str.replace('市', '区')
    df['最高气温'] = df['最高气温'].astype(float)
    fig = main(df, input_)

    return fig


if __name__ == '__main__':
    weather = Weather()
    app.run_server()
