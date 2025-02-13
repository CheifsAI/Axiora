from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
import pandas as pd

# ✅ **1️⃣ Load Wikipedia content and convert it into a knowledge base**
url = "https://en.wikipedia.org/wiki/Data_analysis"  # Replace with your desired article URL
loader = WebBaseLoader(url)
wiki_documents = loader.load()

# ✅ **2️⃣ Split the content into smaller chunks**
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_wiki_docs = text_splitter.split_documents(wiki_documents)

# ✅ **3️⃣ Convert the chunks into embeddings using Ollama**
embedding_model = OllamaEmbeddings(model="ollama-embedding")  # Use the appropriate Ollama model

# ✅ **4️⃣ Create a FAISS vector database**
vector_db = FAISS.from_documents(split_wiki_docs, embedding_model)

# ✅ **5️⃣ Create a retriever**
retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ✅ **6️⃣ Set up the LLM using Ollama**
ollama_model = Ollama(model="mistral")  # Use the available Ollama model

# ✅ **7️⃣ Define the prompt template**
analysis_prompt_template = """
Use the following information from the article to analyze the provided data:
{context}

### Data:
{data_sample}

📊 **Analysis:**
"""

analysis_prompt = PromptTemplate(
    template=analysis_prompt_template,
    input_variables=["context", "data_sample"]
)

# ✅ **8️⃣ Create the RAG-based analysis chain**
analysis_chain = RetrievalQA.from_chain_type(
    llm=ollama_model,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": analysis_prompt}
)

# ✅ **9️⃣ Function to analyze new data using RAG and Wikipedia content**
def analyze_data_with_rag(df):
    # Convert DataFrame into text format
    data_sample = "\n".join([f"{col}: {df[col].astype(str).tolist()[:5]}" for col in df.columns])

    # Run the analysis chain
    result = analysis_chain.invoke({"query": data_sample})

    return result['result']

# ✅ **🔟 Test the analysis on a CSV file**
df = pd.read_csv("Regions.csv")  # Replace with your file
analysis_result = analyze_data_with_rag(df)

print(analysis_result)
