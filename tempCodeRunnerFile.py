import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# إنشاء التطبيق
app = dash.Dash(__name__)

# تصميم الواجهة
app.layout = html.Div([
    html.H1("World Cup Data Visualization"),
    dcc.Dropdown(
        id='chart-type',
        options=[
            {'label': 'Bar Chart - Home Goals', 'value': 'bar'},
            {'label': 'Line Chart - Goals Over Years', 'value': 'line'},
            {'label': 'Scatter Plot - Correlation', 'value': 'scatter'},
            {'label': 'Histogram - Distribution', 'value': 'histogram'}
        ],
        value='bar'
    ),
    dcc.Graph(id='graph-output')
])

# ضبط التفاعل بين الفلتر والشارت
@app.callback(
    Output('graph-output', 'figure'),
    [Input('chart-type', 'value')]
)
def update_chart(chart_type):
    if chart_type == 'bar':
        data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
        fig = px.bar(x=data.index[:10], y=data.values[:10], labels={'x': 'Team', 'y': 'Goals'}, title="Most Goals Scored as Home Team")
    elif chart_type == 'line':
        data = df.groupby("Year")["Home Team Goals"].sum()
        fig = px.line(x=data.index, y=data.values, labels={'x': 'Year', 'y': 'Goals'}, title="Goals Scored Over the Years", markers=True)
    elif chart_type == 'scatter':
        numerical_cols = df.select_dtypes(include=['number']).columns
        if len(numerical_cols) >= 2:
            fig = px.scatter(df, x=numerical_cols[0], y=numerical_cols[1], title=f"Correlation between {numerical_cols[0]} and {numerical_cols[1]}")
        else:
            fig = px.scatter(title="Not enough numerical data for correlation")
    elif chart_type == 'histogram':
        numerical_cols = df.select_dtypes(include=['number']).columns
        if len(numerical_cols) >= 1:
            fig = px.histogram(df, x=numerical_cols[0], title=f"Distribution of {numerical_cols[0]}", nbins=20, marginal="rug")
        else:
            fig = px.histogram(title="Not enough numerical data for distribution")
    else:
        fig = px.bar(title="Invalid Selection")
    
    return fig

# تشغيل التطبيق
if __name__ == '__main__':
    app.run_server(debug=True)