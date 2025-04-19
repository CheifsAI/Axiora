from Charty import Charty
import pandas as pd
charty = Charty()
from OprFuncs import data_describer

sales_data = pd.read_csv("sales.csv")
#supply_chain_data = pd.read_csv("Test_Datasets\supply_chain_data.csv")
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

#question = "What are the total sales across all months?"
question = "What are the total sales by category across all years?"
#question = "What are the most profitable subcategories over the years"
#question = "Which product type have the most availability average "
#question = "What product type have the most Revenue"
# Use separately
#chart_type = charty.select_chart_type(data_info, question)
#print(chart_type)
#columns = charty.select_columns(data_info, question)
#print(columns)
# Or use combined (like original)
chart_type, columns = charty.get_chart_recommendation(data_info,question)
print(chart_type, columns)
""""
["Product type","SKU","Price","Availability","Number of products sold","Revenue generated","Customer demographics","Stock levels",
                  "Supplier  Lead times","Order quantities","Shipping times","Shipping carriers","Shipping costs","Supplier name","Location",
                  "Inventory Lead time","Production volumes","Manufacturing lead time","Manufacturing costs","Inspection results",
                  "Defect rates","Transportation modes","Routes","Costs"]
                                                      """