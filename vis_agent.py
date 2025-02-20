from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms import Ollama
from OprFuncs import data_infer, extract_code, extract_questions
import pandas as pd
from OprFuncs import data_infer,data_describer
# Initialize Ollama
llm = Ollama(model="llama3.2:3b")

dataframe = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
dataframe = dataframe
data_info = data_infer(dataframe)
data_summary = data_describer(dataframe)
data_head = dataframe.head().to_string
guidelines = """▼ Chart Selection Matrix
| Scenario                          | Chart Type      |
|------------------------------------|-----------------|
| Time series analysis               | Line chart      |
| Comparing >3 categories            | Bar chart       |
| Distribution of continuous data    | Histogram       |
| Part-to-whole relationships        | Pie chart       |
| Correlation between 2 variables    | Scatter plot    |
| Multivariate comparison            | Heatmap         |
| Geographical data                  | Choropleth      |

▲ Special Cases:
- Use box plots for statistical distributions
- Use stacked bars for cumulative totals
- Avoid pie charts when >5 categories"""
chart_selection_prompt = PromptTemplate(
    input_variables=["data_info", "data_sample", "data_summary", "guidelines", "question"],
    template="""
    You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_summary}
        Analyze this question to determine the best chart type:
    Question: {question}
    Respond ONLY with the chart type name (line, bar, pie, etc.), your chart type selection is based on knowledge from {guidelines}"""
)
chart_chain = LLMChain(
    llm=llm,
    prompt=chart_selection_prompt
)
def chart_selector(input_text):
    return chart_chain.run(
        question=input_text,
        data_info=data_info,
        data_sample=data_head,
        data_summary=data_summary,
        guidelines=guidelines  
    )

code_gen_prompt = PromptTemplate(
    input_variables=["question", "chart_type", "data_info", "data_sample", "data_summary"],
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
code_chain = LLMChain(llm=llm, prompt=code_gen_prompt)

def code_generator(inputs):
    return code_chain.run(
        question=inputs["question"],
        chart_type=inputs["chart_type"],
        data_info=data_info,
        data_sample=data_head,
        data_summary=data_summary  
    )
tools = [
    Tool(
        name="ChartSelector",
        func=chart_selector,
        description="Determine appropriate chart type for a question"
    ),
    Tool(
        name="CodeGenerator",
        func=lambda x: code_generator({
            "question": x.split("|")[0].strip('"').strip(),
            "chart_type": x.split("|")[1].strip().lower() if "|" in x else "bar"
        }),
        description="Generate Pygal visualization code for specified chart type"
    )
]
agent_prompt = hub.pull("hwchase17/react").partial(
    instructions="""Follow EXACTLY this sequence:
    1. Use ChartSelector ONCE
    2. Use CodeGenerator ONCE
    3. Output FINAL ANSWER with code
    NEVER repeat steps or tools"""
)
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True,
    stop=["\nFINAL ANSWER"]  # Move stop sequence here
)
question = "Show the most teams played as home team off all time"

result = agent_executor.invoke({
    "input": f"""Analyze this question and generate visualization code:
    Question: {question}
    Follow this EXACT format:
    Thought: First analyze the question
    Action: ChartSelector
    Action Input: "{question}"
    Observation: [chart-type]
    Thought: Now generate code
    Action: CodeGenerator
    Action Input: "{question}|[chart-type]"
    FINAL ANSWER:"""
})

print(result["output"])