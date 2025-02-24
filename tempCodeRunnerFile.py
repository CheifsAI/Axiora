import pandas as pd
import pygal
from pygal.style import Style
import re

def extract_number(question):
    numbers = re.findall(r'\d+', question)
    return int(numbers[0]) if numbers else 10

def chart_selector(question, df):
    if "time" in question.lower() and "Year" in df.columns:
        return "line"
    if "correlation" in question.lower() and df.select_dtypes(include=['number']).shape[1] >= 2:
        return "scatter"
    if "distribution" in question.lower() and df.select_dtypes(include=['number']).shape[1] >= 1:
        return "histogram"
    if "part-to-whole" in question.lower() and any(df.dtypes == 'object'):
        return "pie"
    if "goals" in question.lower():
        return "bar"
    return "bar"

def generate_chart(chart_type, df, question):
    theme = Style(colors=["#3498db", "#e74c3c", "#2ecc71", "#f1c40f"])
    filename = "chart.svg"
    top_n = extract_number(question)
    
    if chart_type == "bar":
        chart = pygal.Bar(style=theme, x_label_rotation=45, title=f"Top {top_n} Teams with Most Goals as Home Team")
        data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
        chart.x_labels = data.index[:top_n]
        chart.add("Goals", data.values[:top_n])
        chart.render_to_file(filename)
    
    elif chart_type == "line" and "Year" in df.columns:
        chart = pygal.Line(style=theme, title="Goals Scored Over the Years")
        data = df.groupby("Year")["Home Team Goals"].sum()
        chart.x_labels = map(str, data.index)
        chart.add("Goals", data.values)
        chart.render_to_file(filename)
    
    elif chart_type == "scatter" and df.select_dtypes(include=['number']).shape[1] >= 2:
        numerical_cols = df.select_dtypes(include=['number']).columns[:2]
        chart = pygal.XY(style=theme, title=f"Correlation between {numerical_cols[0]} and {numerical_cols[1]}")
        chart.add("Data", [(row[numerical_cols[0]], row[numerical_cols[1]]) for _, row in df.iterrows()])
        chart.render_to_file(filename)
    
    elif chart_type == "histogram" and df.select_dtypes(include=['number']).shape[1] >= 1:
        data_col = df.select_dtypes(include=['number']).columns[0]
        chart = pygal.Histogram(style=theme, title=f"Distribution of {data_col}")
        chart.add("Distribution", [(1, value, value) for value in df[data_col]])
        chart.render_to_file(filename)
    
    elif chart_type == "pie" and "Home Team Name" in df.columns:
        chart = pygal.Pie(style=theme, title="Percentage of Matches Hosted by Teams")
        data = df["Home Team Name"].value_counts()
        for team, count in data.items():
            chart.add(team, count)
        chart.render_to_file(filename)
    
    print(f"تم إنشاء ملف SVG: {filename}")

def execute_agent(question, df):
    chart_type = chart_selector(question, df)
    generate_chart(chart_type, df, question)

# تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# مثال تشغيل الوكيل بسؤال معين
question = "How have goals scored by home teams changed over the years?"
execute_agent(question, df)
