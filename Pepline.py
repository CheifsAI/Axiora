from Main import *
from Models import llama3b
from OprFuncs import read_file
df = read_file("Test_Datasets\supply_chain_data.csv")
analysis_data(df,llama3b)
questions = quetions_gen(4,llama3b,df)
visual(df,llama3b,questions)
