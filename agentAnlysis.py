from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_community.llms import Ollama
from OprFuncs import data_infer, extract_code, extract_questions
import pandas as pd
import numpy as np
from langchain_ollama import OllamaLLM
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA

llm = Ollama(model="llama3.2:3b")
dataframe = pd.read_csv("Test_Datasets/supply_chain_data.csv")

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

data_sample = dataframe.head().to_string
data_summary = data_describer(dataframe)
data_info = data_infer(dataframe)


def understander(_):
    """Generate dataset understanding"""
    prompt = PromptTemplate.from_template("""
    Analyze this dataset structure:
    {data_info}
    
    Generate a concise summary of:
    1. What business domain this data represents
    2. Key columns and their potential relationships
    3. Possible analysis directions
    """)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run(data_info=data_info)

def retrieval(information):
    """Retrieve relevant KPIs"""
    embeddings = OllamaEmbeddings(model="llama3.2:3b")
    
    try:
        db = FAISS.load_local("faiss_KPIS", embeddings, allow_dangerous_deserialization=True)
    except:
        raise ValueError("FAISS index not found. Please create KPI embeddings first.")
    
    prompt = PromptTemplate(
        template="Context: {context}\nQuestion: {question}",
        input_variables=["context", "question"]
    )
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(),
        chain_type_kwargs={"prompt": prompt}
    )
    
    return qa.run(f"Based on: {information}\nWhat are the most relevant KPIs?")


def analysis_data(kpi):
    """Perform analysis using specified KPI"""
    prompt = PromptTemplate.from_template("""
    Dataset Sample:
    {sample}
    
    Dataset Summary:
    {summary}
    
    Analyze this data focusing on: {kpi}
    Include:
    - Relevant calculations
    - Trends/patterns
    - Actionable insights
    - Visualisation suggestions
    """)
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run({
        "sample": data_sample,
        "summary": data_summary,
        "kpi": kpi
    })
tools = [
    Tool(
        name="DatasetUnderstanding",
        func=understander,
        description="First step: Generates dataset overview. No input needed."
    ),
    Tool(
        name="KPIRetrieval",
        func=retrieval,
        description="Second step: Finds relevant KPIs. Input should be dataset summary."
    ),
    Tool(
        name="DataAnalysis",
        func=analysis_data,
        description="Final step: Performs analysis. Input should be a KPI."
    )
]

agent_prompt = hub.pull("hwchase17/react").partial(
    instructions="""STRICT EXECUTION ORDER:
    1. Use DatasetUnderstanding ONCE
    2. Use KPIRetrieval with previous Observation
    3. Use DataAnalysis with retrieved KPI
    
    Follow EXACTLY this format:
    Thought: [Step reasoning]
    Action: [Tool name]
    Action Input: [Tool input if needed]
    Observation: [Tool result]
    """
)

agent = create_react_agent(llm, tools, agent_prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3,
    handle_parsing_errors=True
)

# Execute analysis
result = agent_executor.invoke({
    "input": "Perform complete analysis of the supply chain dataset. Follow the strict three-step process."
})

print("\nFINAL ANALYSIS:")
print(result["output"])