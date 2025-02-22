import pygal
import pandas as pd
from pygal.style import Style

# 1️⃣ تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# 2️⃣ تحديد نوع الرسم بناءً على السؤال
guidelines = {
    "time series": "line",
    "comparison": "bar",
    "distribution": "histogram",
    "part-to-whole": "pie",
    "correlation": "scatter",
    "multivariate": "heatmap",
    "geographical": "choropleth",
    "goals": "bar"  # إضافة تحليل الأهداف
}

def chart_selector(question):
    for key, chart in guidelines.items():
        if key in question.lower():
            return chart
    return "bar"  # الخيار الافتراضي

# 3️⃣ إنشاء الرسم البياني بناءً على نوع السؤال
def generate_chart(chart_type, df):
    if "goals" in chart_type.lower():
        # حساب إجمالي الأهداف المسجلة كفريق مضيف
        data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
        title = "Most Goals Scored as Home Team"
    else:
        # حساب عدد المباريات المستضافة لكل فريق
        data = df["Home Team Name"].value_counts()
        title = "Most Teams Played as Home Team"

    # إنشاء الرسم البياني
    custom_style = Style(colors=["#3498db", "#e74c3c", "#2ecc71", "#f1c40f"])
    chart = pygal.Bar(style=custom_style, x_label_rotation=45)
    chart.title = title
    chart.x_labels = data.index[:10]  # عرض أفضل 10 فرق فقط
    chart.add("Teams", data.values[:10])
    chart.render_to_file("chart.svg")
    print(f"Chart generated as SVG: chart.svg")

# 4️⃣ تنفيذ الوكيل
def execute_agent(question):
    chart_type = chart_selector(question)
    generate_chart(chart_type, df)

# 📌 تشغيل الوكيل مع مثال سؤال
question = "Which teams have scored the most goals as the home team over the years?"
execute_agent(question)
