from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from OprFuncs import data_infer, extract_code, extract_questions

# Analysis Data
def analysis_data(dataframe,llm):
    data_info = data_infer(dataframe)

    # Prompt and Chain for Analysis Data
    analysis_prompt = '''
    You are a data analyst. You are provided with a dataset about {data_info}
    Here is the dataset structure:
    {data_info}

    Please analyze the data and provide insights about:
    1. Key trends and patterns in the {data_info}.
    2. Any anomalies or outliers in the data.
    3. Recommendations or actionable insights based on the analyzed data.
    '''
    # Define the prompt template
    analysis_template = PromptTemplate(
        input_variables=["data_info","topic"],     
        template=analysis_prompt
    )
    # Create a chain for analysis data
    analysis_chain = LLMChain(llm=llm, prompt=analysis_template)
    

    # Run the analysis chain on the provided data
    analysis = analysis_chain.run(data_info=data_info)
    
    #print analysis
    return(analysis)
    

# Drop Nulls
def drop_nulls(dataframe, llm):
    data_info = data_infer(dataframe)
    
    # Prompt and Chain for dropping nulls
    drop_nulls_prompt = '''
    create a code to drop the nulls from the DataFrame named 'df',
    only include the dropping part and importing pandas,
    insure that inplace = True, no extra context or reading the file.
    '''
    # Define the prompt template
    drop_nulls_template = PromptTemplate(
        input_variables=["data_info"],
        template=drop_nulls_prompt
    )
    # Create a chain for dropping nulls
    drop_nulls_chain = LLMChain(llm=llm, prompt=drop_nulls_template)
    
    # Extracting code for dropping nulls
    drop_nulls_code = extract_code(drop_nulls_chain.run(data_info=data_info))
    
    # Print the code for dropping nulls
    print("Code for dropping nulls:\n", drop_nulls_code)
    
    # Drop null values from the data
    exec_env = {"df": dataframe}
    exec(drop_nulls_code, exec_env)
    updated_df = exec_env["df"]
    return updated_df


# Question Generator
def quetions_gen (num,llm, dataframe):
    data_info = data_infer(dataframe)
    
    # Prompt and Chain for Question Generation
    question_prompt = '''
    create {num} anlysis questions about the following data {data_info}
    '''
    # Define the prompt template
    question_template = PromptTemplate(
        input_variables=["num", "data_info"],
        template=question_prompt
    )
    
    # Create a chain for question generation
    question_chain = LLMChain(
        llm=llm,
        prompt=question_template
    )
    
    # Generate the questions
    questions = question_chain.run(num=num, data_info=data_info)
    
    questions_list = extract_questions(questions)
    
    # Print the generated questions
    return(questions_list)


def visual(dataframe, llm, questions):
    data_info = data_infer(dataframe)
    
    # Prompt for creating visualization code
    visual_prompt = '''
    I already have a DataFrame named 'df'. Generate **correctly formatted** matplotlib code to answer each question in {questions}.
    Ensure the code is **indented properly** and follows Python syntax standards.
    Use the following columns information: {data_info}. Create only the visualization code.
    '''
    
    # Define the prompt template
    visual_template = PromptTemplate(
        input_variables=["data_info", "questions"],
        template=visual_prompt
    )
    
    # Create a chain for generating visualizations
    visual_chain = LLMChain(llm=llm, prompt=visual_template)
    
    # Extracting the visualization code
    viscode = extract_code(visual_chain.run(data_info=data_info, questions=questions))
    
    # Print the generated visualization code
    print("Generated Visualization Code:\n", viscode)
    
    # Execute the visualization code
    exec_env = {"df": dataframe}
    exec(viscode, exec_env)