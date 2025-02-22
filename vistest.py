from flask import Flask, render_template, request
import pygal
import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.llms import Ollama
from OprFuncs import data_infer

app = Flask(__name__)
dataframe = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
data_info = data_infer(dataframe)
data_summary = dataframe.describe().to_string()
data_head = dataframe.head().to_string()

guidelines = """| Scenario                          | Chart Type      |
|------------------------------------|-----------------|
| Time series analysis               | Line chart      |
| Comparing >3 categories            | Bar chart       |
| Distribution of continuous data    | Histogram       |
| Part-to-whole relationships        | Pie chart       |
| Correlation between 2 variables    | Scatter plot    |
| Multivariate comparison            | Heatmap         |
| Geographical data                  | Choropleth      |"""

llm = Ollama(model="llama3.2:3b")
chart_selection_prompt = PromptTemplate(
    input_variables=["data_info", "data_sample", "data_summary", "guidelines", "question"],
    template="""
    You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_summary}
    Analyze this question to determine the best chart type:
    Question: {question}
    Respond ONLY with the chart type name (line, bar, pie, etc.), your chart type selection is based on knowledge from {guidelines}"""
)
chart_chain = LLMChain(llm=llm, prompt=chart_selection_prompt)

def chart_selector(question):
    return chart_chain.run(
        question=question,
        data_info=data_info,
        data_sample=data_head,
        data_summary=data_summary,
        guidelines=guidelines  
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    chart_svg = None
    if request.method == 'POST':
        question = request.form['question']
        chart_type = chart_selector(question)
        
        # Generate Pygal chart
        chart = pygal.Bar() if chart_type == 'bar' else pygal.Pie()
        chart.title = f"Chart for: {question}"
        data = dataframe['Home Team Name'].value_counts()
        chart.x_labels = data.index[:10]
        chart.add('Teams', data.values[:10])
        chart_svg = chart.render_data_uri()
    
    return render_template('index.html', chart_svg=chart_svg)

if __name__ == '__main__':
    app.run(debug=True)
