


#----------------------------------------------------
#pygal library and create many of charts
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
    "goals": "bar"
}

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

def generate_chart(chart_type, df):
    custom_style = Style(colors=["#3498db", "#e74c3c", "#2ecc71", "#f1c40f"])
    charts = []
    
    if chart_type == "bar":
        data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
        title = "Most Goals Scored as Home Team"
        chart = pygal.Bar(style=custom_style, x_label_rotation=45)
        chart.x_labels = data.index[:10]
        chart.add("Goals", data.values[:10])
        charts.append((chart, title))
    
    if "Year" in df.columns:
        data = df.groupby("Year")["Home Team Goals"].sum()
        title = "Goals Scored Over the Years"
        chart = pygal.Line(style=custom_style)
        chart.x_labels = map(str, data.index)
        chart.add("Goals", data.values)
        charts.append((chart, title))
    
    if df.select_dtypes(include=['number']).shape[1] >= 2:
        numerical_cols = df.select_dtypes(include=['number']).columns[:2]
        title = f"Correlation between {numerical_cols[0]} and {numerical_cols[1]}"
        chart = pygal.XY(style=custom_style)
        chart.add("Data", [(row[numerical_cols[0]], row[numerical_cols[1]]) for _, row in df.iterrows()])
        charts.append((chart, title))
    
    if df.select_dtypes(include=['number']).shape[1] >= 1:
        data_col = df.select_dtypes(include=['number']).columns[0]
        title = f"Distribution of {data_col}"
        chart = pygal.Histogram(style=custom_style)
        chart.add("Distribution", [(1, value, value) for value in df[data_col]])
        charts.append((chart, title))
    
    if "Home Team Name" in df.columns:
        data = df["Home Team Name"].value_counts()
        title = "Percentage of Matches Hosted by Teams"
        chart = pygal.Pie(style=custom_style)
        for team, count in data.items():
            chart.add(team, count)
        charts.append((chart, title))
    
    for i, (chart, title) in enumerate(charts):
        chart.title = title
        filename = f"chart_{i}.svg"
        chart.render_to_file(filename)
        print(f"Chart generated as SVG: {filename}")

def execute_agent(question):
    chart_type = chart_selector(question, df)
    generate_chart(chart_type, df)



# 📌 تشغيل الوكيل مع مثال سؤال
question = "Which teams have scored the most goals as the home team over the years?"
execute_agent(question)




#-------------------------------------------------------
# دي مكتبه matplotlib

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1️⃣ تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# إنشاء الشكل والمحاور
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle("Combined Data Analysis")

# 1️⃣ شارت الأعمدة للأهداف المسجلة
if "Home Team Name" in df.columns and "Home Team Goals" in df.columns:
    data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
    sns.barplot(x=data.index[:10], y=data.values[:10], ax=axes[0, 0], palette="Blues")
    axes[0, 0].set_title("Most Goals Scored as Home Team")
    axes[0, 0].set_xticklabels(data.index[:10], rotation=45)

# 2️⃣ شارت الخط الزمني
if "Year" in df.columns and "Home Team Goals" in df.columns:
    data = df.groupby("Year")["Home Team Goals"].sum()
    sns.lineplot(x=data.index, y=data.values, ax=axes[0, 1], marker="o", color="r")
    axes[0, 1].set_title("Goals Scored Over the Years")

# 3️⃣ شارت الانتشار للعلاقة بين عمودين رقميين
numerical_cols = df.select_dtypes(include=['number']).columns
if len(numerical_cols) >= 2:
    sns.scatterplot(x=df[numerical_cols[0]], y=df[numerical_cols[1]], ax=axes[1, 0], alpha=0.5, color="g")
    axes[1, 0].set_title(f"Correlation between {numerical_cols[0]} and {numerical_cols[1]}")

# 4️⃣ شارت التوزيع
if len(numerical_cols) >= 1:
    sns.histplot(df[numerical_cols[0]], ax=axes[1, 1], bins=20, kde=True, color="purple")
    axes[1, 1].set_title(f"Distribution of {numerical_cols[0]}")

# ضبط التخطيط وحفظ الصورة
plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig("combined_chart.png")
plt.show()

print("Combined chart generated as PNG: combined_chart.png")




#----------------------------------------------------------------

import pandas as pd
import pygal
from pygal.style import Style

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

def generate_chart(chart_type, df):
    theme = Style(colors=["#3498db", "#e74c3c", "#2ecc71", "#f1c40f"])
    filename = "chart.svg"
    
    if chart_type == "bar":
        chart = pygal.Bar(style=theme, x_label_rotation=45, title="Most Goals Scored as Home Team")
        data = df.groupby("Home Team Name")["Home Team Goals"].sum().sort_values(ascending=False)
        chart.x_labels = data.index[:10]
        chart.add("Goals", data.values[:10])
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
    generate_chart(chart_type, df)

# تحميل البيانات
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")

# مثال تشغيل الوكيل بسؤال معين
question = "Which teams have scored the most goals as the home team over the years give me top 2 team?"
execute_agent(question, df)



#-----------------------
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
question = "Which are the top 3 teams that have scored the most goals as the home team over the years?"
execute_agent(question, df)
