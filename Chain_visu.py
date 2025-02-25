from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms import Ollama  # Updated import
from langchain.prompts import PromptTemplate
import pandas as pd

# Initialize Ollama LLM (Ensure you have Ollama installed & running)
llm = Ollama(model="llama3.2:3b")  # Change to a different model if needed

def data_describer(dataframe):
    # Get the description of the dataframe
    description = dataframe.describe()
    
    # Convert the description to a string with column names
    description_str = "Data Description:\n"
    for col in description.columns:
        description_str += f"\nColumn: {col}\n"
        description_str += description[col].to_string() + "\n"
    
    # Write the description to a file
    with open("df_description.txt", "w", encoding="utf-8") as f:
        f.write(description_str)
    return description_str

# Load the dataset
dataframe = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
data_info = "Sample dataset information"  # Replace with actual data inference
data_summary = data_describer(dataframe)
data_sample = dataframe.head().to_string()

# 📌 Step 1: Chart Selection Chain
chart_selection_prompt = PromptTemplate(
    input_variables=["data_info", "data_sample", "data_summary", "question"],
    template="""
    You are a data analyst responsible for selecting the most appropriate chart type for a given dataset and question. Use the following chart selection guidelines:

    ▼ Chart Selection Matrix
    | Scenario                          | Chart Type      |
    |------------------------------------|-----------------|
    | Time series analysis               | Line chart      |
    | Comparing >3 categories            | Bar chart       |
    | Distribution of continuous data    | Histogram       |
    | Part-to-whole relationships        | Pie chart       |
    | Correlation between 2 variables    | Scatter plot    |
    | Multivariate comparison            | Heatmap         |
    | Geographical data                  | Choropleth      |
    | Showing both distribution and density| Violin Plot   |
    | Correlation between 3 variables    | Bubble Chart   |
    | Relative importance of regions     | Cartogram      |
    | Showing data with uncertainty values| Error Bar Chart |
    | Showing changes over time          | Waterfall Chart |
    | Flow values; handle complex flows  | Sankey Diagram  | 
    | Comparing multiple metrics across categories| Grouped Bar Chart |

    ▲ Special Cases:
    - Use box plots for statistical distributions
    - Use stacked bars for cumulative totals 
    - Use treemaps for visualizing hierarchical data
    - Use Stacked Area Chart for handling overlapping areas
    - Use Progress Rings/Charts for Showing Progress/Completion
    - Use Proportional Symbol Map for Comparing proportions/rates 
    - Use area charts to avoid misleading representations
    - Avoid clutter and unnecessary visual elements
    - Avoid pie charts when >5 categories

    Analyze the provided dataset information and determine the most suitable chart type.

    Dataset metadata: {data_info}
    Dataset sample: {data_sample}
    Dataset summary: {data_summary}

    Question: {question}

    Respond ONLY with the chart type name (e.g., Line chart, Bar chart, Pie chart, etc.).
    """
)

chart_selection_chain = LLMChain(
    llm=llm,
    prompt=chart_selection_prompt,
    output_key="chart_type"
)

# Step 2: Generate Pygal Code
pygal_code_prompt = PromptTemplate(
    input_variables=["data_info", "data_sample", "data_summary", "question", "chart_type"],
    template="""
    You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_summary}

    Generate Pygal code for {chart_type} chart answering:
    Question: {question}

    Follow these requirements:
    1. Use pandas to process the dataframe, don't read the dataframe, it's already read with the name df
    2. Create Pygal chart object with appropriate config
    3. Add data using dataframe columns
    4. Include proper labels and styling
    5. Save to SVG file
    Example structure:
    import pygal
    from pygal.style import Style
    # Data processing
    data = dataframe['column'].value_counts()
    # Chart configuration
    chart = pygal.Bar(style=Style(...), x_label_rotation=45)
    chart.title = "Chart Title"
    chart.x_labels = data.index
    chart.add('Series', data.values)
    chart.render_to_file('charts/chart.svg')

    Generate code for the current dataset:
    """
)

pygal_code_chain = LLMChain(
    llm=llm,
    prompt=pygal_code_prompt,
    output_key="pygal_code"
)

# Define the SequentialChain
sequential_chain = SequentialChain(
    chains=[chart_selection_chain, pygal_code_chain],
    input_variables=["data_info", "data_sample", "data_summary", "question"],
    output_variables=["chart_type", "pygal_code"]
)

# Example usage
question = "What is the distribution of goals scored in World Cup matches?"
result = sequential_chain({
    "data_info": data_info,
    "data_sample": data_sample,
    "data_summary": data_summary,
    "question": question
})

print("Selected Chart Type:", result["chart_type"])
print("Generated Pygal Code:", result["pygal_code"]) 