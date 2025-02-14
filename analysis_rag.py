from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import pandas as pd
import fitz  # PyMuPDF لقراءة ملفات PDF
import os  # للتحقق من وجود الملف
from DataAnalyzer import DataAnalyzer  # Importing the class from another file

FAISS_DB_PATH = "faiss_index"

# 1. تحميل ملف القواعد (PDF) من الذاكرة
def load_analysis_rules_from_memory(pdf_content):
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    rules = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rules += page.get_text()
    return rules

# 2. إنشاء وثائق (Documents) من القواعد
def create_documents_from_rules(rules):
    return [Document(page_content=rules)]

# 3. تدريب نظام RAG على القواعد
def train_rag_system(documents):
    if os.path.exists(FAISS_DB_PATH):
        print("\n🔄 Loading existing FAISS index...")
        vector_db = FAISS.load_local(FAISS_DB_PATH, OllamaEmbeddings(model="llama2"))
    else:
        print("\n🛠️ Generating new embeddings and saving FAISS index...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)
        embedding_model = OllamaEmbeddings(model="llama2")
        vector_db = FAISS.from_documents(texts, embedding_model)
        vector_db.save_local(FAISS_DB_PATH)
    
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    llm = Ollama(model="llama2")
    prompt_template = """
    Use the following piece of context to answer the question asked.
    Please try to provide the answer only based on the context.

    {context}
    Question: {question}

    Helpful Answers:
    """
    prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
    retrievalQA = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    return retrievalQA, llm

# 4. تحميل ملف CSV جديد
def load_csv(file_path):
    return pd.read_csv(file_path)

# الخطوات الرئيسية
if __name__ == "__main__":
    # Load rules from PDF file
    with open("storying.pdf", "rb") as file:
        pdf_content = file.read()
    
    documents = load_analysis_rules_from_memory(pdf_content)
    
    # Train RAG model
    retrievalQA, llm = train_rag_system(documents)
    
    # Load CSV data
    df = load_csv("Regions.csv")  
    
    # Create DataAnalyzer instance
    analyzer = DataAnalyzer(df, llm=llm)
    
    # Perform data analysis
    query = analyzer.analysis_data()
    
    # Use RetrievalQA to answer the query
    result = retrievalQA.run(query)
    
    # Display the final result
    print("Final Analysis Result:")
    print(result)