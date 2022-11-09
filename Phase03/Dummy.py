from dash import Dash, html, dcc, Input, Output, State
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url
import dash_bootstrap_components as dbc
import dash_extensions as de
import dash_daq as daq

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
theme_change = ThemeChangerAIO(aio_id="theme", radio_props={"persistence": True}, button_props={"color": "danger","children": "Change Theme"})

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(theme_change, style={'padding': 0, 'border':'none', 'border-color': 'black', 'background': 'none'}),
    ],
    brand="IOT SMART HOME",
    color="dark",
    dark=True,
    sticky="top"
)

sidebar = html.Div(
    [
    html.H1('User Profile', style={'text-align': 'center'}),
    dbc.CardBody([
            dbc.CardImg(src="assets/minion.jpg", className="test m-b-25 img-radius rounded-circle"),
            html.H6("Username"),
            html.H4("Favorites: "),
            html.H6("Humidity"),
            html.H6("Temperature"),
            html.H6("Light Intensity"),
    ])
    ]
)

content = html.Div(
    [
        html.P('Content')
    ]
)

app.layout = dbc.Container(
    [
        dbc.Row(navbar),
        dbc.Row(
            [
                dbc.Col(sidebar, width=3, className='bg-light'),
                dbc.Col(content, width=9)
                ],
            style={"height": "100vh"}
            ),
        ],
    fluid=True
)


if __name__ == "__main__":
    app.run_server(debug=True)