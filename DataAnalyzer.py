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
from modelEXT.PygalCodeComponents import PygalCodeComponents
from langchain.output_parsers import PydanticOutputParser
from DatabaseManager import DatabaseManager
class DataAnalyzer:
    def __init__(self,dataframe,llm):
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_summary = data_describer(dataframe)
        self.data_sample = dataframe.head().to_string()
        self.data_cols = ", ".join(dataframe.columns)
        self.db = DatabaseManager()
        self.session_id = None
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
        self.db.saveMemory(sessID=self.session_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=formatted_analysis_prompt,
                           response=analysis,
                           chat=False)
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
            self.db.saveMemory(sessID=self.session_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=formatted_question_prompt,
                           response="\n".join(questions_list),
                           chat=False)

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
        self.db.saveMemory(sessID=self.session_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=question,
                           response=response,
                           chat=True)

        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response))
        return response
    

    def visual(self,report, questions_list: list):
        code_template = """import pygal
        from pygal.style import RedBlueStyle

        data = df["{column}"].value_counts()
        chart = pygal.{chart_type}(style=RedBlueStyle, x_label_rotation=45)
        chart.title = '{chart_title}'
        chart.x_labels = [str(x) for x in data.index.tolist()]  # Convert all labels to strings
        chart.add('{column}', data.values)  # Use original column name for legend
        chart.render_to_file('{report}/{chart_title}.svg')
        """
        viscodes = []
        for question in questions_list:
            vis_resp = self._chart_select_chain(question)
            print(vis_resp)
            
            chart_type = vis_resp['chart_type']
            chart_title = vis_resp['chart_title']
            column = vis_resp['columns']
            
            # Clean up column name and chart title
            if column in self.dataframe.columns:  # Verify column exists
                chart_title = f"{column} Distribution"  # Use simple distribution title
            
            viscode = code_template.format(
                chart_type=chart_type,
                chart_title=chart_title,
                column=column,
                report=report
            )
            viscode = viscode.strip()
            viscodes.append(viscode)
        
        return viscodes
    
    
    def _chart_select_chain(self, question):
       # data_info = self.data_info
       # data_sample = self.data_sample
       # data_summary = self.data_summary
        data_cols = self.data_cols
        llm = self.llm

        chart_type_mapping = {
            "bar chart": "Bar",
            "bar": "Bar",
            "line chart": "Line",
            "line": "Line",
            "pie chart": "Pie",
            "pie": "Pie",
            "histogram": "Histogram",
            "stackedbar": "StackedBar",
            "stacked bar": "StackedBar",
            "radar": "Radar",
            "box": "Box",
        }

        guidelines = """▼ Chart Selection Matrix
    | Scenario                           | Chart Type      | When to Use                             |
    |------------------------------------|-----------------|-----------------------------------------|
    | Time series analysis               | Line            | Track trends over time (years, months)  |
    | Comparing >3 categories            | Bar             | Compare discrete values across groups   |
    | Distribution of data               | Histogram       | Show frequency distribution of data     |
    | Comparing 2-5 categories           | Pie             | Show proportions (limit to 5 categories)|
    | Part-to-whole relationships        | StackedBar      | Show cumulative totals and components   |
    | Multivariate comparison            | Radar           | Compare multiple quantitative variables |
    | Statistical distribution analysis  | Box             | Show quartiles and outliers             |

    ▲ Special Cases:
    - Use box plots for statistical distributions
    - Use stacked bars for cumulative totals 
    - Use Progress Rings/Charts for progress/completion
    - Use Proportional Symbol Map for proportions/rates 
    - Use area charts to avoid misleading representations
    - Avoid pie charts when >5 categories"""

        chart_selection_prompt = PromptTemplate(
            input_variables=["data_cols", "question"],
            template="""Based on the available columns: {data_cols}
            Select the most appropriate visualization for this question: {question}
            based on {guidelines} 
            
            Respond in this exact format:
            chart_type: [type]
            column: [single column name]
            
            The column MUST be one of the available columns listed above.
            The chart_type should be one of: bar, line, pie, histogram, stackedbar, radar, box"""
        )

        chart_selection_chain = LLMChain(
            llm=llm,
            prompt=chart_selection_prompt,
            output_key="chart_selection_result" 
        )
        
        response = chart_selection_chain({
            "data_cols": data_cols,
            "question": question,
            "guidelines":guidelines
        })
        
        result = response["chart_selection_result"].strip()
        
        # Parse the response
        chart_type = None
        column = None
        
        for line in result.split('\n'):
            if 'chart_type:' in line.lower():
                chart_type = line.split(':')[1].strip().lower()
            elif 'column:' in line.lower():
                column = line.split(':')[1].strip()
        
        # Validate and clean up
        if not chart_type or not column:
            chart_type = "Bar"  # default
            column = self.dataframe.columns[0]  # fallback to first column
            
        chart_type = chart_type_mapping.get(chart_type, "Bar")
        
        # Verify column exists in dataframe
        if column not in self.dataframe.columns:
            print(f"Warning: Column '{column}' not found. Available columns: {self.data_cols}")
            column = self.dataframe.columns[0]  # fallback to first column
            
        return {
            "chart_type": chart_type,
            "chart_title": column,  # Use column name as chart title
            "columns": column
        }