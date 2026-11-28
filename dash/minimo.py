from dash import Dash, Input, Output, dcc, html

app = Dash(__name__)

app.layout = html.Div([
    html.H3("Callback minimo"),
    dcc.Dropdown(
        id="color",
        options=["Rojo", "Azul", "Verde"],
        value="Azul",
    ),
    html.Div(id="salida"),
])


@app.callback(
    Output("salida", "children"),
    Input("color", "value"),
)
def mostrar(color):
    return f"Elegiste: {color}"


if __name__ == "__main__":
    app.run(debug=True, port=8051)
