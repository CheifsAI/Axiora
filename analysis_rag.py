from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OllamaEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
import pandas as pd
import fitz  # PyMuPDF لقراءة ملفات PDF
import io  # لقراءة الملف من الذاكرة

# 1. تحميل ملف القواعد (PDF) من الذاكرة
def load_analysis_rules_from_memory(pdf_content):
    # فتح ملف PDF من الذاكرة
    doc = fitz.open(stream=pdf_content, filetype="pdf")
    rules = ""
    
    # استخراج النصوص من كل صفحة
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        rules += page.get_text()
    
    return rules

# 2. إنشاء وثائق (Documents) من القواعد
def create_documents_from_rules(rules):
    documents = []
    # إضافة القواعد كوثيقة
    documents.append(Document(page_content=rules))
    return documents

# 3. تدريب نظام RAG على القواعد
def train_rag_system(documents):
    # تقسيم النصوص إلى أجزاء أصغر
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)
    
    # تهيئة نموذج التضمين (Embedding) باستخدام Ollama
    embedding_model = OllamaEmbeddings(model="llama2")  # استخدام OllamaEmbeddings
    
    # إنشاء متجر المتجهات (Vector Store)
    vector_db = FAISS.from_documents(texts, embedding_model)
    
    # تهيئة Retriever
    retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})
    
    # تهيئة نموذج اللغة (LLM) باستخدام Ollama
    llm = Ollama(model="llama2")  # استخدام Ollama بدلاً من HuggingFaceHub
    
    # إنشاء سلسلة RetrievalQA
    prompt_template = """
    Use the following piece of context to answer the question asked.
    Please try to provide the answer only based on the context.

    {context}
    Question: {question}

    Helpful Answers:
    """
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    retrievalQA = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": prompt}
    )
    
    return retrievalQA

# 4. تحميل ملف CSV جديد
def load_csv(file_path):
    df = pd.read_csv(file_path)
    return df

# 5. تحليل ملف CSV بناءً على القواعد
def analyze_csv_with_rules(retrievalQA, df):
    # تحويل البيانات إلى وثائق
    documents = []
    for _, row in df.iterrows():
        page_content = " | ".join([f"{col}: {str(row[col])}" for col in df.columns])
        documents.append(Document(page_content=page_content))
    
    # تحليل البيانات باستخدام RAG
    results = []
    for doc in documents:
        query = f"Analyze this data based on the rules: {doc.page_content}"
        result = retrievalQA.invoke({"query": query})
        results.append(result['result'])
    
    return results

# الخطوات الرئيسية
if __name__ == "__main__":
    # قراءة ملف PDF كبايتس
    with open("storying.pdf", "rb") as file:
        pdf_content = file.read()
    
    # تحميل ملف القواعد (PDF) من الذاكرة
    rules = load_analysis_rules_from_memory(pdf_content)
    
    # إنشاء وثائق من القواعد
    documents = create_documents_from_rules(rules)
    
    # تدريب نظام RAG على القواعد
    retrievalQA = train_rag_system(documents)
    
    # تحميل ملف CSV جديد
    csv_path = r"D:\My-Githup\Axiora\ agent\Regions.csv"  # استخدام raw string
    df = load_csv(csv_path)
    
    # تحليل ملف CSV بناءً على القواعد
    analysis_results = analyze_csv_with_rules(retrievalQA, df)
    
    # عرض النتائج
    for i, result in enumerate(analysis_results):
        print(f"Analysis for row {i+1}: {result}")