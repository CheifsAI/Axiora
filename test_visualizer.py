import pandas as pd
from Visualizer import Visualizer
import os

def test_visualizations():
    # Create output directory
    os.makedirs("test_output", exist_ok=True)

    # Load sample data
    try:
        df = pd.read_csv('supply_chain_data/supply_chain_data.csv')
    except FileNotFoundError:
        # Create sample data if file doesn't exist
        df = pd.DataFrame({
            'Category': ['A', 'B', 'A', 'C', 'B', 'C'] * 10,
            'Values': [10, 20, 15, 25, 30, 35] * 10,
            'Sales': [100, 150, 120, 200, 180, 220] * 10,
            'Growth': [0.1, 0.2, 0.15, 0.25, 0.3, 0.35] * 10
        })

    # Initialize visualizer
    viz = Visualizer(df)

    # Test different chart types
    test_cases = [
        {
            'title': 'Category Distribution',
            'chart_type': 'Bar',
            'columns': ['Category'],
            'output': 'test_output/bar_chart.html'
        },
        {
            'title': 'Sales Over Time',
            'chart_type': 'Line',
            'columns': ['Sales', 'Values'],
            'output': 'test_output/line_chart.html'
        },
        {
            'title': 'Value Distribution',
            'chart_type': 'Histogram',
            'columns': ['Values'],
            'output': 'test_output/histogram.html'
        },
        {
            'title': 'Category Breakdown',
            'chart_type': 'Pie',
            'columns': ['Category'],
            'output': 'test_output/pie_chart.html'
        },
        {
            'title': 'Sales vs Growth',
            'chart_type': 'Scatter',
            'columns': ['Sales', 'Growth'],
            'output': 'test_output/scatter_plot.html'
        },
        {
            'title': 'Stacked Category Values',
            'chart_type': 'StackedBar',
            'columns': ['Category', 'Values'],
            'output': 'test_output/stacked_bar.html'
        }
    ]

    # Generate each chart type
    for test in test_cases:
        print(f"\nGenerating {test['chart_type']} chart...")
        result = viz.generate_visualization(
            question=test['title'],
            output_path=test['output'],
            columns=test['columns'],
            chart_type=test['chart_type']
        )
        
        if result['success']:
            print(f"✓ Successfully generated {test['chart_type']} chart: {result['output_path']}")
        else:
            print(f"✗ Failed to generate {test['chart_type']} chart: {result['message']}")

if __name__ == "__main__":
    test_visualizations()
    print("\nTest complete! Check the test_output directory for the generated charts.") 