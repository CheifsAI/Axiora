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
def quetions_gen (num,llm, data_info):
    questions = llm.invoke(f"create {num} anlysis questions about {data_info}")
    return questions
def visual (dataframe, llm, questions):
    data_info = data_infer(dataframe)
    viscode = llm.invoke(f"I already have a dataframe named 'df', Only create matplotlib code for each question in {questions} with the columns {data_info} in one python script")
    visualcode = extract_code(viscode)
    return exec(visualcode)