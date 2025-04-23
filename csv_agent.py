""" import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_csv_agent

llm = OllamaLLM(model="llama3.2:3b")

agent = create_csv_agent(
    llm,
    'sales.csv',
    verbose=True,
    allow_dangerous_code=True
)

response = agent.invoke("What are the most profitable subcategories over the years?")
print(response)"""
import pandas as pd
from langchain.document_loaders.csv_loader import CSVLoader
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_csv_agent



llm = OllamaLLM(model="phi3.5:3.8b")

agent = create_csv_agent(
    llm,
    'Test_Datasets\sales.csv',
    verbose=True,
    allow_dangerous_code=True  
)

response = agent.invoke("What are the most profitable subcategories over the years?")
print(response)