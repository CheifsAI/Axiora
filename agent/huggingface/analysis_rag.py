from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
import pandas as pd

# 1️⃣ تحميل النصوص من PDF وتخزينها في قاعدة FAISS
loader = PyPDFLoader("storying.pdf")
documents = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = splitter.split_documents(documents)
embeddings = OllamaEmbeddings(model="llama2")
db = FAISS.from_documents(docs, embeddings)
retriever = db.as_retriever()

# 2️⃣ إعداد RetrievalQA كنموذج RAG
llm = ChatOllama(model="llama2",)
prompt_template = PromptTemplate(
    template="""
    Use the following context to answer the question:
    {context}
    
    Question: {question}
    
    Answer:
    """,
    input_variables=["context", "question"]
)
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": prompt_template}
)

# 3️⃣ تحميل وتحليل بيانات CSV
class DataAnalyzer:
    def __init__(self, file_path):
        self.df = pd.read_csv(file_path)

    def analysis_data(self):
        summary = self.df.describe().to_string()
        return f"Data Analysis Summary:\n{summary}"

    def analyze_regions(self):
        region_analysis = self.df.groupby("Region").mean().to_string()
        return f"Regional Analysis:\n{region_analysis}"

analyzer = DataAnalyzer("Regions.csv")
data_insights = analyzer.analysis_data()
region_analysis = analyzer.analyze_regions()

# 4️⃣ استعلام النظام RAG باستخدام البيانات المحللة
query = f"Based on the following data insights: {data_insights}\n{region_analysis}, apply the rules from the document to generate insights."
response = rag_chain.invoke({"query": query})

# 5️⃣ إخراج النتائج
print("\n🔍 Final Analysis Result:")
print(f"📊 Data Insights: \n{data_insights}\n")
print(f"🤖 RAG Insights: \n{response['result']}")
