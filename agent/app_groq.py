import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the Groq API key
groq_api_key = os.getenv('GROQ_API_KEY')

# Initialize session state
if "vector" not in st.session_state:
    
    # Initialize embeddings
    st.session_state.embedding = OllamaEmbeddings(model="llama2")

    # Load documents
    st.session_state.loader = WebBaseLoader("https://docs.smith.langchain.com/")
    st.session_state.docs = st.session_state.loader.load()
    
    # Split documents
    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs[:50])
    
    # Initialize vector database
    st.session_state.vector_db = FAISS.from_documents(st.session_state.final_documents, st.session_state.embedding)
    
# Initialize Groq Chat
st.title("ChatAbdul_Jawad Demo")

# Initialize Groq LLM
llm = ChatGroq(groq_api_key=groq_api_key, model_name="mixtral-8x7b-32768")

# Define the prompt template
prompt = ChatPromptTemplate.from_template(
"""
Answer the questions based on the provided context only.
Please provide the most accurate response based on the question
<context>
{context}
<context>
Questions:{input}
"""
)

# Create document chain
document_chain = create_stuff_documents_chain(llm, prompt)

# Create retriever
retriever = st.session_state.vector_db.as_retriever()

# Create retrieval chain
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# User input
prompt = st.text_input("input your prompt here")

if prompt:
    with st.spinner('Processing your request...'):
        start = time.process_time()
        try:
            response = retrieval_chain.invoke({"input": prompt})
            st.write(response['answer'])
            
            with st.expander("📄 Document Similarity Search"):
                if "context" in response:
                    for i, doc in enumerate(response["context"]):
                        st.write(f"Document {i + 1}:")
                        st.write(doc.page_content)
                        st.write("--------------------------------")
                else:
                    st.write("⚠️ No relevant documents found.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
        finally:
            st.info(f"Response time: {time.process_time() - start} seconds")