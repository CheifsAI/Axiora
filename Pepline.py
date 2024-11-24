from Main import scvpd,data_infer,summerizer, llama3b
df = scvpd("titanic.csv")
summerizer(df,llama3b)