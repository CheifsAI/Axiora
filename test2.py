from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms import Ollama

# Initialize Ollama
llm = Ollama(model="llama3.2:3b")

# ----- Tool 1: Chart Type Selector -----
chart_selection_prompt = PromptTemplate(
    input_variables=["question"],
    template="""Analyze this question to determine the best matplotlib chart type:
    Question: {question}
    Respond ONLY with the chart type name (line, bar, pie, etc.), yor knolwadge is from {guidlines}"""
)

chart_chain = LLMChain(llm=llm, prompt=chart_selection_prompt)

def chart_selector(input_text):
    return chart_chain.run(question=input_text)

# ----- Tool 2: Code Generator -----
code_gen_prompt = PromptTemplate(
    input_variables=["question", "chart_type"],
    template="""Generate matplotlib code for {chart_type} chart answering:
    Question: {question}
    Include sample data, labels, and plt.show()"""
)

code_chain = LLMChain(llm=llm, prompt=code_gen_prompt)

def code_generator(inputs):
    return code_chain.run(
        question=inputs["question"],
        chart_type=inputs["chart_type"]
    )

# ----- Create Tools -----
tools = [
    Tool(
        name="ChartSelector",
        func=chart_selector,
        description="Determine appropriate chart type for a question"
    ),
    Tool(
        name="CodeGenerator",
        func=lambda inputs: code_generator(inputs),
        description="Generate matplotlib code for specified chart type"
    )
]

# ----- Agent Setup -----
agent_prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ----- Execution -----
question = "Show the most teams played as home team"
result = agent_executor.invoke({
    "input": f"""Answer this question in 3 steps: 
    1. Choose chart type
    2. Generate code
    3. Output result
    
    Question: {question}"""
})

print(result["output"])