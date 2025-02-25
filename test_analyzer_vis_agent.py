import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
question1 = "Who is the most teams won with condition?"
analyzer = DataAnalyzer(llm=llama3b,dataframe=df)
agentcode = analyzer.visual(questions_list=question1)
print(agentcode)