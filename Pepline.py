from Main import summerizer, nulldrop
from OprFuncs import csvpd
from Models import llama3b
df = csvpd("WorldCupMatches.csv")
summerizer(df,llama3b)
nulldrop(df,llama3b)
