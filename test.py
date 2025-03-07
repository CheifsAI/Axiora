import pandas as pd
from DataAnalyzer import DataAnalyzer
from LLM import llama3b,deepseek
import os

styles=["RedBlueStyle",
"BlueStyle",
"DarkSolarizedStyle",
"LightColorizedStyle",
"DarkStyle",
"CleanStyle",
"TurquoiseStyle",
"DarkColorizedStyle",
"LightSolarizedStyle"]
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
questions = ["Who is the most teams played as home team?","Who is the most teams played as away team?"]
analyzer = DataAnalyzer(llm=deepseek,dataframe=df)
report_name="test_charts"
os.makedirs(report_name, exist_ok=True)  
agentcode = analyzer.visual(questions_list=questions,style=styles[0],report=report_name)
print(agentcode)
for code in agentcode:
     code =  "\n".join(line.strip() for line in code.splitlines() if line.strip())
     print(code)
     #compiled_code = compile(code, "<string>", "exec")
     exec(code)
     print(f"{code}\n\n\n\n\n\n\n")