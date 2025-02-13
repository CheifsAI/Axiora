from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from langchain_community.llms import Ollama
import numpy as np
import pandas as pd
from DataAnalyzer import DataAnalyzer

# Load the dataset
file_path = "Regions.csv"
df = pd.read_csv(file_path)

# Create LangChain Document objects
documents = [
    Document(page_content=" | ".join([f"{col}: {str(row[col])}" for col in df.columns]))
    for _, row in df.iterrows()
]

# Initialize the text splitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Split the documents into chunks
text_split = text_splitter.split_documents(documents)

# Initialize the embedding model
embedding_model = OllamaEmbeddings(model="llama3.2:3b")

# Initialize the vector database
vector_db = FAISS.from_documents(text_split, embedding_model)

# Initialize the retriever
retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Initialize the Ollama LLM
ollama_model = Ollama(model="mistral")

# Define the prompt template
prompt_template = """
Use the following piece of context to answer the question asked.
Please try to provide the answer only based on the context

{context}
Question: {question}

Helpful Answers:
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# Create the RetrievalQA chain
retrievalQA = RetrievalQA.from_chain_type(
    llm=ollama_model,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt}
)

# Initialize the DataAnalyzer
analyzer = DataAnalyzer(df, llm=ollama_model)  # Use Ollama instead of HuggingFace

# Define the query
query = analyzer.analysis_data()

# Call the QA chain with our query
result = retrievalQA.invoke({"query": query})
print(result['result'])