from OprFuncs import data_infer, extract_code
def summerizer (dataframe,llm):
    data_info = data_infer(dataframe)
    summary = llm.invoke(f"summarize{data_info}")
    return print(summary)
def nulldrop (dataframe,llm):
    response = llm.invoke(f"create a code to drop the nulls from the DataFrame named 'df', only include the dropping part, insure that inplace = True, no extra context or reading the file.")
    dropping_nulls_code = extract_code(response)
    print("Extracted Code:\n", dropping_nulls_code)
    exec_env = {"df": dataframe}
    exec(dropping_nulls_code, exec_env)
    updated_df = exec_env["df"]
    return updated_df.info()