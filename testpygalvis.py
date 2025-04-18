from PygalVisualizer import PygalVisualizer
import pandas as pd
sales_data = pd.read_csv("sales.csv")
# Initialize with your DataFrame
visualizer = PygalVisualizer(sales_data)

# Set a custom style
visualizer.set_style('DarkSolarizedStyle')

# Generate and save visualization
result = visualizer.generate_visualization(
    question="sales by product across all months",
    output_path="visualizations/sales_months.svg",
    columns=['sales', 'orderdate_month'],  # Optional override
    chart_type='Line',  # Optional override
    width=1200,
    height=800
)

if result['success']:
    print(f"Success! {result['message']}")
    print("Generated code:\n", result['code'])
else:
    print(f"Failed: {result['message']}")