import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
import textwrap

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
analyzer = DataAnalyzer(llm=llama3b,dataframe=df)
agentcode = analyzer.visual(questions_list=questions,style=styles[0])
print(agentcode)
for code in agentcode:
     code =  "\n".join(line.strip() for line in code.splitlines() if line.strip())
     print(code)
     #compiled_code = compile(code, "<string>", "exec")
     exec(code)
     print(f"{code}\n\n\n\n\n\n\n")