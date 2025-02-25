import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
questions = ["Who is the most teams played as home team?","Who is the most teams played as away team?"]

analyzer = DataAnalyzer(llm=llama3b,dataframe=df)
agentcode = analyzer.visual(questions_list=questions)
for i in agentcode:
    print(f"{i}\n\n\n\n\n\n\n")