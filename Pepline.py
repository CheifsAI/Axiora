from Main import csvpd,data_infer,summerizer, llama3b, nulldrop
df = csvpd("WorldCupMatches.csv")
# summerizer(df,llama3b)
nulldrop(df,llama3b)