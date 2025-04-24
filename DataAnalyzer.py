import pandas as pd
from typing import Dict, List, Tuple
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from OprFuncs import *
#from langchain.schema.runnable import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#from langchain.agents import AgentExecutor, Tool, create_react_agent
#from langchain import hub
import re
#from modelEXT.PygalCodeComponents import PygalCodeComponents
#from langchain.output_parsers import PydanticOutputParser
from DatabaseManager import DatabaseManager
from langchain_experimental.agents import create_pandas_dataframe_agent

class DataAnalyzer:
    def __init__(self,dataframe,llm,user_id=None):
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_description = data_describer(dataframe)
        self.data_sample = dataframe.head().to_string()
        self.data_cols = ", ".join(dataframe.columns)
        self.db = DatabaseManager()
        self.report_id = None
        self.memory = []
        
        if user_id:
            self.user_id = user_id
            self.user_context = self.db.get_user_context(user_id)
            if self.user_context:
                self.memory.append(HumanMessage(content=f"User Context: {self.user_context}"))
        else:
            self.user_context = None

    def analysis_data(self):
        data_info = self.data_info
        data_sample = self.data_sample
        data_description = self.data_description

        analysis_template = '''
        You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_description}
        4. User_context: {user_context}

        Please analyze the data and provide insights about:
        1. Key trends and patterns.
        3. Recommendations or actionable insights based on the analyzed data.
        '''
        analysis_prompt = PromptTemplate(
            input_variables=["data_info", "data_sample", "data_description", "user_context"],
            template=analysis_template
        )
        
        analysis_chain = analysis_prompt | self.llm

        self.analysis = analysis_chain.invoke({
            "data_info": data_info,
            "data_sample": data_sample,
            "data_description": data_description,
            "user_context":self.user_context or "No prior context available"
        })

        formatted_analysis_prompt = analysis_template.format(data_info=data_info,data_sample=data_sample,
                                                             data_description=data_description,
                                                             user_context=self.user_context)
        self.memory.append(HumanMessage(content=formatted_analysis_prompt))
        self.memory.append(AIMessage(content=self.analysis))
        self.db.saveMemory(reportID=self.report_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=formatted_analysis_prompt,
                           response=self.analysis,
                           chat=False)
        self.generate_user_context()
        return self.analysis        

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
        data_description = self.data_description

        question_prompt = f"""
        You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_description} 
        Create {num} analysis questions about the dataset.

        Please format each question on a new line, starting with a number, as in this example:
        1. question 1?
        2. question 2?
        """

        question_template = PromptTemplate(
            input_variables=["num", "data_info", "data_sample", "data_description"],
            template=question_prompt
        )

        question_chain = question_template | self.llm

        try:
            generated_questions = question_chain.invoke({
                "num": num,
                "data_info": data_info,
                "data_sample": data_sample,
                "data_description": data_description
            })

            # Ensure the response is properly encoded
            if isinstance(generated_questions, str):
                generated_questions = generated_questions.encode('utf-8', 'replace').decode('utf-8')

            print("Raw LLM Output:", repr(generated_questions))

            if not generated_questions.strip():
                print("Warning: LLM did not generate any questions.")
                return []

            # Use the improved extraction function
            questions_list = extract_questions(generated_questions)

            print("Extracted Questions List:", questions_list)

            # Trim or handle missing questions
            if len(questions_list) > num:
                questions_list = questions_list[:num]
            elif len(questions_list) < num:
                print(f"Warning: Expected {num} questions, but got {len(questions_list)}")

            # Store in memory
            formatted_question_prompt = question_template.format(
                num=num,
                data_info=data_info,
                data_sample=data_sample,
                data_description=data_description
            )
            self.memory.append(HumanMessage(content=formatted_question_prompt))
            self.memory.append(AIMessage(content="\n".join(questions_list)))
            self.db.saveMemory(reportID=self.report_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=formatted_question_prompt,
                           response="\n".join(questions_list),
                           chat=False)

            return questions_list

        except Exception as e:
            print(f"Error generating questions: {str(e)}")
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
        self.db.saveMemory(reportID=self.report_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=question,
                           response=response,
                           chat=True)

        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response))
        return response
    

    def select_chart_type(self, question: str) -> str:
        self.chart_type_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at selecting chart types for data visualization. Strictly follow these rules:
            
            1. CHART SELECTION GUIDE:
            - For comparing categories: Bar 
            - For trends over time: Line
            - For parts of a whole: Pie (few categories)
            - For relationships: Scatter
            - For the distribution of a numirecal variable: Histogram
            
            3. OUTPUT FORMAT (EXACTLY):
            chart_type: [Bar|Line|Pie|Scatter|Histogram]
            
            Data Description: {data_description}
            Available Columns: {columns}
            Sample Data: {sample_data}
            Question: {question}
            
            Respond ONLY with:
            chart_type: [chart_type]""")
        ])

        """Select only the chart type based on the question and data."""
        self.llm.temperature = 0.3
        chain = self.chart_type_prompt | self.llm
        response = chain.invoke({
            "data_description": self.data_description,
            "columns": self.data_cols,
            "sample_data": self.data_sample,
            "question": question
        })
        self.llm.temperature = 0.7
        # Parse response
        chart_match = re.search(r'chart_type:\s*([a-zA-Z]+)', response, re.IGNORECASE)
        chart_type = chart_match.group(1) if chart_match else None
        
        # Validate
        allowed_charts =  {
            'Bar', 'Line', 'Histogram', 
            'Pie', 'Scatter'
        }
        return chart_type if chart_type in allowed_charts else 'Bar'
    
    def select_columns(self, question: str) -> List[str]:
        self.columns_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at selecting relevant columns for data visualization. Strictly follow:
            
            1. COLUMN SELECTION RULES:
            - Focus on columns mentioned in the question
            - What is being measured (numerical columns)
            - What is being compared/grouped by (categorical columns)
            - Any time dimensions for trends
            - Never suggest columns not in Available Columns
            
            2. OUTPUT FORMAT (EXACTLY):
            columns: [exact_column_name1, exact_column_name2]
            
            Data Description: {data_description}
            Available Columns: {columns}
            Sample Data: {sample_data}
            Question: {question}
            
            Respond ONLY with:
            columns: [column1, column2]""")
        ])

        """"Select only the relevant columns based on the question and data."""
        self.llm.temperature = 0.3
        chain = self.columns_prompt | self.llm
        response = chain.invoke({
            "data_description": self.data_description,
            "columns":self.data_cols,
            "sample_data": self.data_sample,
            "question": question
        })
        self.llm.temperature = 0.7
        # Parse response
        cols_match = re.search(r'columns:\s*\[([^\]]+)\]', response)
        if cols_match:
            columns = [col.strip() for col in cols_match.group(1).split(',')]
        else:
            # Fallback parsing
            cols_line = next((line for line in response.split('\n') if line.startswith('columns:')), '')
            columns = [col.strip() for col in cols_line.replace('columns:', '').split(',') if col.strip()]
        
        # Validate columns exist in data
        available_cols = self.dataframe.columns.tolist()
        return [col for col in columns if col in available_cols]
    
    def get_chart_recommendation(self, question: str) -> Tuple[str, List[str]]:
        """Combined recommendation (maintaining original interface)"""
        chart_type = self.select_chart_type(question)
        columns = self.select_columns(question)
        return chart_type, columns
    
    def generate_user_context(self):
        if not self.user_id:
            return "No user ID provided"
            
        context_template = """
        Generate a concise user profile context based on:

        User's existing context: {existing_context}
        Current analysis: {current_analysis}
        Conversation history: {conversation_summary}
        Focus on:
        - Key analysis interests
        - Frequently asked about metrics
        - Data domains of interest
        
        Format as bullet points, max 5 items.
        """
        
        conversation = "\n".join([msg.content for msg in self.memory[-4:]])
        
        context_prompt = PromptTemplate(
            template=context_template,
            input_variables=["existing_context", "current_analysis", "conversation_summary"]
        )
        
        new_context = (context_prompt | self.llm).invoke({
            "existing_context": self.user_context or "No prior context available",
            "current_analysis": self.analysis,
            "conversation_summary": conversation
        })
        
        self.db.update_user_context(userID=self.user_id, new_context=new_context)
        return new_context
