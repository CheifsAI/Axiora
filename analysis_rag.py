from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings  # استبدال HuggingFaceBgeEmbeddings بـ Ollama
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.llms import Ollama  # استبدال HuggingFaceHub بـ Ollama
import pandas as pd

# ✅ **1️⃣ تحميل الكتاب وتحويله إلى قاعدة معرفة**
pdf_loader = PyPDFLoader("data_analysis_book.pdf")  # استبدل باسم كتابك
book_documents = pdf_loader.load()

# ✅ **2️⃣ تقسيم الكتاب إلى مقاطع صغيرة**
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
split_book_docs = text_splitter.split_documents(book_documents)

# ✅ **3️⃣ تحويل المقاطع إلى متجهات باستخدام نموذج Ollama**
embedding_model = OllamaEmbeddings(model="ollama-embedding")  # استخدم النموذج المناسب لـ Ollama

# ✅ **4️⃣ إنشاء قاعدة بيانات متجهية FAISS**
vector_db = FAISS.from_documents(split_book_docs, embedding_model)

# ✅ **5️⃣ إنشاء نظام الاسترجاع (Retriever)**
retriever = vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# ✅ **6️⃣ إعداد نموذج LLM باستخدام Ollama**
ollama_model = Ollama(model="mistral")  # استخدم النموذج المتاح لديك في Ollama

# ✅ **7️⃣ إعداد القالب النصي (Prompt)**
analysis_prompt_template = """
استخدم المعلومات التالية من الكتاب لتحليل البيانات المقدمة:
{context}

### البيانات:
{data_sample}

📊 **التحليل:**
"""

analysis_prompt = PromptTemplate(
    template=analysis_prompt_template,
    input_variables=["context", "data_sample"]
)

# ✅ **8️⃣ إنشاء سلسلة تحليل البيانات باستخدام RAG**
analysis_chain = RetrievalQA.from_chain_type(
    llm=ollama_model,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True,
    chain_type_kwargs={"prompt": analysis_prompt}
)

# ✅ **9️⃣ دالة لتحليل البيانات الجديدة باستخدام RAG والكتاب**
def analyze_data_with_rag(df):
    # تحويل البيانات إلى نصوص
    data_sample = "\n".join([f"{col}: {df[col].astype(str).tolist()[:5]}" for col in df.columns])

    # تشغيل سلسلة التحليل
    result = analysis_chain.invoke({"query": data_sample})

    return result['result']

# ✅ **🔟 تجربة التحليل على ملف CSV**
df = pd.read_csv("Regions.csv")  # استبدل باسم ملفك
analysis_result = analyze_data_with_rag(df)

print(analysis_result)
