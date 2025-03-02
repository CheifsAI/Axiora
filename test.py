import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
questions = ["Who is the most teams played as home team?","Who is the most teams played as away team?"]
analyzer = DataAnalyzer(llm=llama3b,dataframe=df)
agentcode = analyzer._chart_select_chain(question=questions[0])
print(agentcode)
#for code in agentcode:
 #   exec(code)
  #  print(f"{code}\n\n\n\n\n\n\n")