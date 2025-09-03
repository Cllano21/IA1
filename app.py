# app.py
import pandas as pd
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import os

# ================================
#  Cargar datos desde el CSV
# ================================
csv_path = "data_for_analyst_takehome__Jan2025.csv"
df = pd.read_csv(csv_path)

# Asegurar que la columna de fechas sea datetime
df["trip_completed_at"] = pd.to_datetime(df["trip_completed_at"])

# Convertimos a dólares (ya que la columna tiene "cents")
df["boost_dollars"] = df["cumulative_boost_amount_cents"]

# ================================
#  Agregación de datos
# ================================
df_agg = df.groupby(
    ["origin_metro_area_name", df["trip_completed_at"].dt.date]
).agg(
    total_boost=("boost_dollars", "sum"),
    avg_boost=("boost_dollars", "mean"),
    trips=("trip_id", "count")
).reset_index().rename(columns={"trip_completed_at": "date"})

# ================================
#  Dash App
# ================================
app = Dash(__name__)
app.layout = html.Div([
    html.H1("Boost Monitoring Dashboard"),
    html.P("Monitor cumulative boosts per market over time."),
    
    dcc.Dropdown(
        id="market-dropdown",
        options=[{"label": m, "value": m} for m in df_agg["origin_metro_area_name"].unique()],
        value=[df_agg["origin_metro_area_name"].unique()[0]],  # valor inicial
        multi=True
    ),
    
    dcc.Graph(id="boost-line-chart")
])

# ================================
#  Callbacks
# ================================
@app.callback(
    Output("boost-line-chart", "figure"),
    Input("market-dropdown", "value")
)
def update_chart(selected_markets):
    filtered = df_agg[df_agg["origin_metro_area_name"].isin(selected_markets)]
    fig = px.line(
        filtered,
        x="date",
        y="total_boost",
        color="origin_metro_area_name",
        markers=True,
        title="Total Boost ($) per Market Over Time"
    )
    fig.update_layout(yaxis_title="Total Boost ($)", xaxis_title="Date")
    return fig

# ================================
#  Run server en Render
# ================================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=True, host="0.0.0.0", port=port)
