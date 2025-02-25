from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms import Ollama  # Updated import
from langchain.prompts import PromptTemplate
import pandas as pd

# Initialize Ollama LLM (Ensure you have Ollama installed & running)
llm = Ollama(model="llama3.2:3b")  

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
    | Scenario                          | Chart Type      | when to use                            |
    |------------------------------------|----------------|----------------------------------------|
    | Time series analysis               | Line            | Track trends over time (years, months)
    | Comparing >3 categories            | Bar             | Compare discrete values across groups
    | Distribution of data               | Histogram       | Show frequency distribution of data
    | Comparing 2-5 categories           | Pie             | Show proportions (limit to 5 categories)
    | Part-to-whole relationships        | StackedBar      | Show cumulative totals and components
    | Multivariate comparison            | Radar           | Compare multiple quantitative variables
    | Statistical distribution analysis  | Box             | Show quartiles and outliers
    | Frequency distribution over time   | DateY           | Date-based time series

    ▲ Special Cases:
    - Use box plots for statistical distributions
    - Use stacked bars for cumulative totals 
    - Use Progress Rings/Charts for Showing Progress/Completion
    - Use Proportional Symbol Map for Comparing proportions/rates 
    - Use area charts to avoid misleading representations
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
    input_variables=["chart_type", "data_info", "data_sample", "data_summary", "question"],
    template="""
    You are provided with:
    1. Dataset metadata: {data_info}
    2. Dataset sample: {data_sample}
    3. Dataset summary: {data_summary}

    Generate COMPLETE Pygal code for {chart_type} chart answering:
    Question: {question}
    
    Generate Pygal code with these strict requirements:
    1. Use pandas to process the dataframe, don't read the dataframe, it's already read with the name df
    2. Start with: chart = pygal.{{chart_type}}()  # Exact match
    3. Add data using dataframe columns
    3. Configure axis labels using df column names
    4. Save to 'charts/result.svg'

    Question: {question}

    Example for {chart_type}:
    chart = pygal.{chart_type}(x_label_rotation=45)
    chart.title = "Chart Title"
    data = df['column'].value_counts()
    chart.add('Series', data.values)
    chart.render_to_file('charts/result.svg')

    Actual code:
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
question = "How has the average number of goals per match evolved across different World Cup tournaments over time?"
result = sequential_chain({
    "data_info": data_info,
    "data_sample": data_sample,
    "data_summary": data_summary,
    "question": question
})

print("Selected Chart Type:", result["chart_type"])
print("Generated Pygal Code:", result["pygal_code"]) 