import pandas as pd
import io
import re
import os

def data_infer(dataframe):   
    buffer = io.StringIO()
    dataframe.info(buf=buffer)
    data_info = buffer.getvalue()
    with open("df_info.txt", "w",
            encoding="utf-8") as f:  
        f.write(data_info)
    return data_info
def extract_code(input_text):
    result = re.search(r'```.*?\n(.*?)\n```', input_text, re.DOTALL)
    code = result.group(1) if result else input_text
    code_lines = code.splitlines()
    cleaned_code = "\n".join(line.strip() for line in code_lines)
    return cleaned_code.strip()


def read_file(path):
    _, extension = os.path.splitext(path)    
    if extension == ".csv":
        df = pd.read_csv(path)
    elif extension in [".xls", ".xlsx"]:
        df = pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file format: {extension}")
    return df

def extract_questions(generated_text):
    # Split the text by lines and filter out empty lines
    lines = [line.strip() for line in generated_text.split('\n') if line.strip()]
    
    # Extract questions (assuming each question starts with a number and a dot)
    questions = []
    for line in lines:
        if line[0].isdigit() and '.' in line:
            questions.append(line.split('. ', 1)[1])  # Split on the first occurrence of '. ' and take the second part
    
    return questions