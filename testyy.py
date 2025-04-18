from Charty import Charty
import pandas as pd
charty = Charty()
from OprFuncs import data_describer

sales_data = pd.read_csv("sales.csv")
description = data_describer(sales_data)
data_sample = sales_data.head().to_string()
data_cols = ", ".join(sales_data.columns)

#analyzer = DataAnalyzer(sales_data,llama3b)
data_info = {
    "description": description,
    "data_cols": ["orderid","Customer", "Name","shipmode","sales","quantity","discount","profit","segment","region",
                  "state","subcategory","category","orderdate_day","orderdate_weekday","orderdate_month",
                  "orderdate_year","shipdate_day","shipdate_month","shipdate_year","preparationtime"],
    "head": data_sample
}

question = "What are the total sales across all months?"
# Use separately
#chart_type = charty.select_chart_type(data_info, question)
#print(chart_type)
columns = charty.select_columns(data_info, question)
print(columns)
# Or use combined (like original)
#chart_type, columns = charty.get_chart_recommendation(data_info, "Show product sales distribution")