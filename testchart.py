from DataAnalyzer import DataAnalyzer 
from ChartSelector import ChartSelector
import pandas as pd
from LLM import llama3b
from OprFuncs import data_describer

sales_data = pd.read_csv("sales.csv")
description = data_describer(sales_data)
data_sample = sales_data.head().to_string()
data_cols = ", ".join(sales_data.columns)

#analyzer = DataAnalyzer(sales_data,llama3b)
data_info = {
    "description": description,
    "data_cols": ["orderid","Customer" "Name","shipmode","sales","quantity","discount","profit","segment","region",
                  "state","subcategory","category","orderdate_day","orderdate_weekday","orderdate_month",
                  "orderdate_year","shipdate_day","shipdate_month","shipdate_year","preparationtime"],
    "head": data_sample
}

question = "What are the total sales by product across all months?"

selector = ChartSelector()
chart_type, columns = selector.get_chart_recommendation(data_info, question)

print(f"Recommended chart type: {chart_type}")
print(f"Columns to use: {columns}")
