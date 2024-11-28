from Models import llama3b
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from OprFuncs import csvpd
from OprFuncs import data_infer, extract_code


llm = llama3b

# Summarize Data
def summerizer(dataframe, llm):
    data_info = data_infer(dataframe)

    # Prompt and Chain for summarization
    summary_prompt = '''
    Summarize the following dataframe information:
    {data_info}
    '''
    summary_template = PromptTemplate(
        input_variables=["data_info"],
        template=summary_prompt
    )
    summary_chain = LLMChain(llm=llm, prompt=summary_template)

    summary = summary_chain.run(data_info=data_info)
    print("Summary:\n", summary)
    

# Drop Nulls
def drop_nulls(dataframe, llm):
    data_info = data_infer(dataframe)
    
    # Prompt and Chain for dropping nulls
    drop_nulls_prompt = '''
    create a code to drop the nulls from the DataFrame named 'df',
    only include the dropping part,
    insure that inplace = True, no extra context or reading the file.
    '''
    drop_nulls_template = PromptTemplate(
        input_variables=["data_info"],
        template=drop_nulls_prompt
    )
    drop_nulls_chain = LLMChain(llm=llm, prompt=drop_nulls_template)
    
    # Extracting code for dropping nulls
    drop_nulls_code = extract_code(drop_nulls_chain.run(data_info=data_info))
    print("Code for dropping nulls:\n", drop_nulls_code)
    
    exec_env = {"df": dataframe}
    exec(drop_nulls_code, exec_env)
    updated_df = exec_env["df"]
    return updated_df.info()


# Question Generator
def quetions_gen (num,llm, dataframe):
    data_info = data_infer(dataframe)
    
    # Prompt and Chain for Question Generation
    question_prompt = '''
    create {num} anlysis questions about the following data {data_info}
    '''
    
    question_template = PromptTemplate(
        input_variables=["num", "data_info"],
        template=question_prompt
    )
    
    question_chain = LLMChain(
        llm=llm,
        prompt=question_template
    )
    
    # Generate the questions
    questions = question_chain.run(num=num, data_info=data_info)
    
    print("Generated Questions:\n", questions)