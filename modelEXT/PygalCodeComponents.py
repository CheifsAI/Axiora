from pydantic import BaseModel, Field

class PygalCodeComponents(BaseModel):
   # imports: str = Field(description="Pygal imports including style. Example: 'import pygal\nfrom pygal.\style\ import \style\'")
    imports: str = Field(description="Pygal import")
    data_preparation: str = Field(description="Data processing using value_counts(). Example: 'data = df[\"column\"].value_counts()'")
    chart_instantiation: str = Field(description="Chart creation withrotation. Example: 'chart = pygal.Bar(x_label_rotation=45)'")
    labels_config: str = Field(description="X-axis labels from data index. Example: 'chart.x_labels = data.index'")
    series_addition: str = Field(description="Adding data series with label. Example: 'chart.add(\"chart title\", data.values)'")
    rendering: str = Field(description="File rendering command. Example: 'chart.render_to_file(\"output.svg\")'")

