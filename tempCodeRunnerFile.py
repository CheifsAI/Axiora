import pygal
import pandas as pd
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

# 1️⃣ تحميل البيانات
# استبدل بمسار بياناتك الفعلي
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

guidelines = {
    "time series": "line",
    "comparison": "bar",
    "distribution": "histogram",
    "part-to-whole": "pie",
    "correlation": "scatter",
    "multivariate": "heatmap",
    "geographical": "choropleth"
}

# 2️⃣ تحديد نوع الرسم بناءً على السؤال
def chart_selector(question):
    for key, chart in guidelines.items():
        if key in question.lower():
            return chart
    return "bar"  # الخيار الافتراضي

# 3️⃣ توليد كود Pygal بناءً على الرسم المختار
def generate_pygal_code(chart_type, df):
    if chart_type == "bar":
        code = """
import pygal
from pygal.style import Style

data = df['Home Team Name'].value_counts()
chart = pygal.Bar(style=Style(colors=['#3498db']), x_label_rotation=45)
chart.title = "Most Teams Played as Home Team"
chart.x_labels = data.index
chart.add('Teams', data.values)
chart.render_to_file('chart.svg')
        """
    elif chart_type == "pie":
        code = """
import pygal
from pygal.style import Style

data = df['Home Team Name'].value_counts()
chart = pygal.Pie(style=Style(colors=['#e74c3c', '#3498db', '#2ecc71']))
chart.title = "Most Teams Played as Home Team"
for team, count in data.items():
    chart.add(team, count)
chart.render_to_file('chart.svg')
        """
    else:
        code = ""  # أنواع أخرى يمكن إضافتها لاحقًا
    return code

# 4️⃣ تنفيذ ال Agent
def execute_agent(question):
    chart_type = chart_selector(question)
    pygal_code = generate_pygal_code(chart_type, df)
    exec(pygal_code, globals())  # تنفيذ الكود لتوليد الصورة
    print(f"Chart generated as SVG: chart.svg")

# 📌 تشغيل الوكيل مع مثال سؤال
question = "Which teams have scored the most goals as the home team over the years?"
execute_agent(question)
