""" import pandas as pd
from langchain_ollama import OllamaLLM
from langchain_experimental.agents import create_csv_agent

df = pd.read_csv('sales.csv')
print(df)

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

loader = CSVLoader(file_path='sales.csv') 
data = loader.load()

df = pd.DataFrame([doc.page_content for doc in data])  
print(df)

llm = OllamaLLM(model="llama3.2:3b")

agent = create_csv_agent(
    llm,
    'sales.csv',
    verbose=True,
    allow_dangerous_code=True  
)

response = agent.invoke("What are the most profitable subcategories over the years?")
print(response)