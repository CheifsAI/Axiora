from langchain_community.llms import Ollama
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
def extract_code(input_text):
    result = re.search(r'```.*?\n(.*?)\n```', input_text, re.DOTALL)
    code = result.group(1) if result else input_text
    code_lines = code.splitlines()
    cleaned_code = "\n".join(line.strip() for line in code_lines)
    return cleaned_code.strip()
llama3b = Ollama(model="llama3.2:3b")
codem = Ollama(model="granite-code:3b")
def csvpd(path):
     df = pd.read_csv(path)
     return df
def nulldrop (dataframe,llm):
    response = llm.invoke(f"create a code to drop the nulls from the DataFrame named 'df', only include the dropping part, insure that inplace = True, no extra context or reading the file.")
    dropping_nulls_code = extract_code(response)
    print("Extracted Code:\n", dropping_nulls_code)
    exec_env = {"df": dataframe}
    exec(dropping_nulls_code, exec_env)
    updated_df = exec_env["df"]
    return updated_df.info()