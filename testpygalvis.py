from PygalVisualizer import PygalVisualizer
import pandas as pd
#sales_data = pd.read_csv("sales.csv")
supply_chain_data = pd.read_csv("Test_Datasets\supply_chain_data.csv")
# Initialize with your DataFrame
visualizer = PygalVisualizer(supply_chain_data)

# Set a custom style
visualizer.set_style('DarkSolarizedStyle')

# Generate and save visualization
result = visualizer.generate_visualization(
    question="sales by product across all months",
    output_path="visualizations/product_revenue.svg",
    columns=['Number of products sold', 'Product type'],  # Optional override
    chart_type='Bar',  # Optional override
    width=1200,
    height=800
)

if result['success']:
    print(f"Success! {result['message']}")
    print("Generated code:\n", result['code'])
else:
    print(f"Failed: {result['message']}")