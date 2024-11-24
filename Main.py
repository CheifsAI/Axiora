from langchain.llms import Ollama
import pandas as pd
import io
import re
def data_infer(dataframe):   
    buffer = io.StringIO()
    dataframe.info(buf=buffer)
    data_info = buffer.getvalue()
    with open("df_info.txt", "w",
            encoding="utf-8") as f:  
        f.write(data_info)
    return data_info
def summerizer (dataframe,llm):
    data_info = data_infer(dataframe)
    summary = llm.invoke(f"summarize{data_info}")
    return print(summary)
def extract_code(input) :
        result = re.search(r'```.*?\n(.*?)\n```', input, re.DOTALL)
        result = result.group(1) if result else input
        return result