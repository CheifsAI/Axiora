import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from OprFuncs import *
from langchain.schema.runnable import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
import re


class DataAnalyzer:
    def __init__(self,dataframe,llm):
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_summary = data_describer(dataframe)
        self.data_sample = dataframe.head().to_string
        self.memory = []

    def analysis_data(self):
        data_info = self.data_info
        data_sample = self.data_sample
        data_summary = self.data_sample

        analysis_prompt = '''
        You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_summary} 

        Please analyze the data and provide insights about:
        1. Key trends and patterns.
        3. Recommendations or actionable insights based on the analyzed data.
        '''
        analysis_template = PromptTemplate(
            input_variables=["data_info","data_sample"],
            template=analysis_prompt
        )
        
        analysis_chain = LLMChain(llm=self.llm, prompt=analysis_template)

        
        analysis = analysis_chain.run(data_info=data_info,data_sample=data_sample,data_summary=data_summary)

        formatted_analysis_prompt = analysis_prompt.format(data_info=data_info,data_sample=data_sample,data_summary=data_summary)
        self.memory.append(HumanMessage(content=formatted_analysis_prompt))
        self.memory.append(AIMessage(content=analysis))

        
        return analysis        

    # Drop Nulls
    def drop_nulls(self):
        data_info = self.data_info
        
        
        drop_nulls_prompt = '''
        create a code to drop the nulls from the DataFrame named 'df',
        only include the dropping part and importing pandas,
        insure that inplace = True, no extra context or reading the file.
        '''
        
        drop_nulls_template = PromptTemplate(
            input_variables=["data_info"],
            template=drop_nulls_prompt
        )
        
        drop_nulls_chain = LLMChain(llm=self.llm, prompt=drop_nulls_template)
        
        
        drop_nulls_code = extract_code(drop_nulls_chain.run(data_info=data_info,))
        
        
        print("Code for dropping nulls:\n", drop_nulls_code)

        self.memory.append(HumanMessage(content=drop_nulls_prompt))
        self.memory.append(AIMessage(content=drop_nulls_code))
        
        
        exec_env = {"df": self.dataframe}
        exec(drop_nulls_code, exec_env)
        updated_df = exec_env["df"]
        return updated_df


    def questions_gen(self, num):
        data_info = self.data_info
        data_sample = self.data_sample
        data_summary = self.data_sample

        question_prompt = f"""
        You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_summary} 
        Create {num} analysis questions about the dataset.

        Please format each question on a new line, starting with a number, as in this example:
        1. What is the average price?
        2. How does revenue correlate with stock levels?
        """

        question_template = PromptTemplate(
            input_variables=["num", "data_info", "data_sample", "data_summary"],
            template=question_prompt
        )

        question_chain = question_template | self.llm

        try:
            generated_questions = question_chain.invoke({
                "num": num,
                "data_info": data_info,
                "data_sample": data_sample,
                "data_summary": data_summary
            })

            print("🔹 Raw LLM Output:", repr(generated_questions))

            if not generated_questions.strip():
                print("⚠️ LLM did not generate any questions.")
                return []

            # Use the improved extraction function
            questions_list = extract_questions(generated_questions)

            print("🟢 Extracted Questions List:", questions_list)

            # Trim or handle missing questions
            if len(questions_list) > num:
                questions_list = questions_list[:num]
            elif len(questions_list) < num:
                print(f"⚠️ Warning: Expected {num} questions, but got {len(questions_list)}")

            # Store in memory
            formatted_question_prompt = question_template.format(
                num=num,
                data_info=data_info,
                data_sample=data_sample,
                data_summary=data_summary
            )
            self.memory.append(HumanMessage(content=formatted_question_prompt))
            self.memory.append(AIMessage(content="\n".join(questions_list)))

            return questions_list

        except Exception as e:
            print(f"❌ Error generating questions: {e}")
            return []

    
    def chat(self,question):
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a data analyst.",
                    ),
                    MessagesPlaceholder(variable_name="memory"),
                    ("human", "{input}"),
                    ]
                    )
        chain = prompt_template | self.llm

        response = chain.invoke({"input": question, "memory":self.memory})
        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response))
        return response
    

    def visual(self, questions_list: list):
       viscodes = []
       for question in questions_list:
           vis_resp = self._visual_chain(question)
           viscode = extract_code(vis_resp)
           if viscode:
               viscodes.append(viscode)
               #exec(viscode) 
       return viscodes
    
    
    def _visual_chain(self,question):
        data_info = self.data_info
        data_sample = self.data_sample
        data_summary = self.data_summary
        llm = self.llm

        guidelines = """▼ Chart Selection Matrix
    | Scenario                           | Chart Type      | when to use                             |
    |------------------------------------|-----------------|-----------------------------------------|
    | Time series analysis               | Line            | Track trends over time (years, months)  |
    | Comparing >3 categories            | Bar             | Compare discrete values across groups   |
    | Distribution of data               | Histogram       | Show frequency distribution of data     |
    | Comparing 2-5 categories           | Pie             | Show proportions (limit to 5 categories)|
    | Part-to-whole relationships        | StackedBar      | Show cumulative totals and components   |
    | Multivariate comparison            | Radar           | Compare multiple quantitative variables |
    | Statistical distribution analysis  | Box             | Show quartiles and outliers             |
    | Frequency distribution over time   | DateY           | Date-based time series                  |

    ▲ Special Cases:
    - Use box plots for statistical distributions
    - Use stacked bars for cumulative totals 
    - Use Progress Rings/Charts for Showing Progress/Completion
    - Use Proportional Symbol Map for Comparing proportions/rates 
    - Use area charts to avoid misleading representations
    - Avoid pie charts when >5 categories"""
        chart_selection_prompt = PromptTemplate(
            input_variables=["data_info", "data_sample", "data_summary", "question"],
            template="""
            You are a data analyst responsible for selecting the most appropriate chart type for a given dataset:
            Dataset metadata: {data_info}
            Dataset sample: {data_sample}
            Dataset summary: {data_summary}
            Use {guidelines} to determine the most suitable chart type for this question : {question}
            Respond ONLY with the chart type name (e.g., Line chart, Bar chart, Pie chart, etc.).
            """)
        chart_selection_chain = LLMChain(
            llm=llm,
            prompt=chart_selection_prompt,
            output_key="chart_type"
            )
        pygal_code_prompt = PromptTemplate(
            input_variables=["chart_type", "data_info", "data_sample", "data_summary", "question"],
            template="""
            You are provided with:
            1. Dataset metadata: {data_info}
            2. Dataset sample: {data_sample}
            Generate COMPLETE Pygal code for {chart_type} chart answering:
            Question: {question}
    
            Generate Pygal code with these strict requirements:
            1. NEVER CREATE OR IMPORT DATAFRAMES - one exists as 'df'
            2. NO DATA IMPORT STATEMENTS (no pandas.read_csv)
            3. Ensure you are using the column names from {data_sample}
            4. Start with: chart = pygal.{{chart_type}}()
            5. Add data using dataframe columns
            6. Configure axis labels using df column names
            7. Save to 'charts/chartname.svg'

            Question: {question}

            use this structure:
            # df is existing
            chartname = pygal.{chart_type}(x_label_rotation=45)
            chart.title = "Chart Title"
            data = df['column'].value_counts()
            chart.add('Series', data.values)
            chart.render_to_file('charts/chartname.svg')

            Actual code:
            """)
        pygal_code_chain = LLMChain(
            llm=llm,
            prompt=pygal_code_prompt,
            output_key="pygal_code"
            )
        sequential_chain = SequentialChain(
            chains=[chart_selection_chain, pygal_code_chain],
            input_variables=["guidelines","data_info", "data_sample", "data_summary", "question"],
            output_variables=["chart_type", "pygal_code"]
            )
        
        vis_chain_result = sequential_chain({
            "guidelines": guidelines,
            "data_info": data_info,
            "data_sample": data_sample,
            "data_summary": data_summary,
            "question": question
            })
        return vis_chain_result['pygal_code']