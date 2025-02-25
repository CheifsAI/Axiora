import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
question1 = "How has the average number of goals per match evolved across different World Cup tournaments over time?"
analyzer = DataAnalyzer(llm=llama3b,dataframe=df)
agentcode = analyzer.visual(questions_list=question1)
print(agentcode)