from Main import summerizer, nulldrop
from OprFuncs import csvpd
from Main import drop_nulls
from Models import llama3b
df = csvpd("Test_Datasets\WorldCupMatches.csv")
#summerizer(df,llama3b)
#nulldrop(df,llama3b)
drop_nulls(df,llama3b)