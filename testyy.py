from Charty import Charty
import pandas as pd
charty = Charty()
from OprFuncs import data_describer

#sales_data = pd.read_csv("sales.csv")
supply_chain_data = pd.read_csv("sales.csv")
description = data_describer(supply_chain_data)
data_sample = supply_chain_data.head().to_string()
data_cols = ", ".join(supply_chain_data.columns)

#analyzer = DataAnalyzer(sales_data,llama3b)
data_info = {
    "description": description,
    "data_cols": ["Product type","SKU","Price","Availability","Number of products sold","Revenue generated","Customer demographics","Stock levels",
                  "Supplier  Lead times","Order quantities","Shipping times","Shipping carriers","Shipping costs","Supplier name","Location",
                  "Inventory Lead time","Production volumes","Manufacturing lead time","Manufacturing costs","Inspection results",
                  "Defect rates","Transportation modes","Routes","Costs"],
    "head": data_sample
}

#question = "What are the total sales across all months?"
#question = "What are the total sales across all years?"
#question = "What are the most profitable subcategories over the years"
question = "Which product type have the most availability average "
#question = "What product type have the most Revenue"
# Use separately
#chart_type = charty.select_chart_type(data_info, question)
#print(chart_type)
#columns = charty.select_columns(data_info, question)
#print(columns)
# Or use combined (like original)
chart_type, columns = charty.get_chart_recommendation(data_info, "Show product sales distribution")
print(chart_type, columns)