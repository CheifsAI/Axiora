import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Load the Groq API key
groq_api_key = os.environ['GROQ_API_KEY']

# Initialize session state
if "vector" not in st.session_state:
    
    # Initialize embeddings
    st.session_state.embedding = OllamaEmbeddings()

    # Load documents
    st.session_state.loader = WebBaseLoader("https://docs.smith.langchain.com/")
    st.session_state.docs = st.session_state.loader.load()
    
    # Split documents
    st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
    
    # Initialize vector database
    st.session_state.vector_db = FAISS.from_documents(st.session_state.final_documents, st.session_state.embedding)