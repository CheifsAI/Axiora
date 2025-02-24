import pandas as pd
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from OprFuncs import *
from langchain.schema.runnable import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub

class DataAnalyzer:
    def __init__(self,dataframe,llm):
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_describtion = data_describer(dataframe)
        self.data_head = dataframe.head().to_string
        self.memory = []

    def analysis_data(self):
        data_info = self.data_info
        data_sample = self.data_head
        data_summary = self.data_describtion

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






    import re

    def questions_gen(self, num):
        data_info = self.data_info
        data_sample = self.data_head
        data_summary = self.data_describtion

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





    def visual(self, questions_list):
       agentres = self._visual_agent(questions_list)
       viscode = extract_code(agentres)
       if viscode:
           return viscode
           #exec(viscode) 
       else:
           print("Error: No valid code generated.")
    
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
    
    def _visual_agent(self,question):
        data_info = self.data_info
        data_sample = self.data_head
        data_summary = self.data_describtion
        llm = self.llm
        guidelines = """▼ Chart Selection Matrix
        | Scenario                          | Chart Type      |
        |------------------------------------|-----------------|
        | Time series analysis               | Line chart      |
        | Comparing >3 categories            | Bar chart       |
        | Distribution of continuous data    | Histogram       |
        | Part-to-whole relationships        | Pie chart       |
        | Correlation between 2 variables    | Scatter plot    |
        | Multivariate comparison            | Heatmap         |
        | Geographical data                  | Choropleth      |

        ▲ Special Cases:
        - Use box plots for statistical distributions
        - Use stacked bars for cumulative totals
        - Avoid pie charts when >5 categories"""
        chart_selection_prompt = PromptTemplate(
            input_variables=["data_info", "data_sample", "data_summary", "guidelines", "question"],
            template="""
            You are a data analyst. You are provided with:
                1. Dataset metadata: {data_info}
                2. Dataset sample: {data_sample}
                3. Dataset summary: {data_summary}
                Analyze this question to determine the best chart type:
            Question: {question}
            Respond ONLY with the chart type name (line, bar, pie, etc.), your chart type selection is based on knowledge from {guidelines}"""
        )
        chart_chain = LLMChain(
            llm=llm,
            prompt=chart_selection_prompt
        )
        def chart_selector(input_text):
            return chart_chain.run(
                question=input_text,
                data_info=data_info,
                data_sample=data_sample,
                data_summary=data_summary,
                guidelines=guidelines  
            )

        code_gen_prompt = PromptTemplate(
            input_variables=["question", "chart_type", "data_info", "data_sample", "data_summary"],
            template="""
            You are provided with:
                1. Dataset metadata: {data_info}
                2. Dataset sample: {data_sample}
                3. Dataset summary: {data_summary}

            Generate COMPLETE Pygal code for {chart_type} chart answering:
            Question: {question}

            Follow these requirements:
            1. Use pandas to process the dataframe, don't read the dataframe, it's already read with the name df
            2. Create Pygal chart object with appropriate config
            3. Add data using dataframe columns
            4. Include proper labels and styling
            5. Save to SVG file

            Example structure:
            ```import pygal
            data = df['column'].value_counts()
            chart = pygal.Bar(x_label_rotation=45)
            chart.title = "Chart Title"
            chart.x_labels = data.index
            chart.add('Series', data.values)
            chart.render_to_file('charts/chart.svg')```

            Generate code for the current dataset: df
            """
        )
        code_chain = LLMChain(llm=llm, prompt=code_gen_prompt)

        def code_generator(inputs):
            return code_chain.run(
                question=inputs["question"],
                chart_type=inputs["chart_type"],
                data_info=data_info,
                data_sample=data_sample,
                data_summary=data_summary  
            )
        tools = [
            Tool(
                name="ChartSelector",
                func=chart_selector,
                description="Determine appropriate chart type for a question"
            ),
            Tool(
                name="CodeGenerator",
                func=lambda x: code_generator({
                    "question": x.split("|")[0].strip('"').strip(),
                    "chart_type": x.split("|")[1].strip().lower() if "|" in x else "bar"
                }),
                description="Generate Pygal visualization code for specified chart type"
            )
        ]
        agent_prompt = hub.pull("hwchase17/react").partial(
            instructions="""Follow EXACTLY this sequence:
            1. Use ChartSelector ONCE
            2. Use CodeGenerator ONCE
            3. Output FINAL ANSWER after code
            NEVER repeat steps or tools"""
        )
        agent = create_react_agent(llm, tools, agent_prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            #max_iterations=5,
            handle_parsing_errors=True,
            stop=["</code>"]  
        )

        result = agent_executor.invoke({
            "input": f"""Analyze this question and generate visualization code:
            Question: {question}
            Follow this EXACT format:
            Thought: First analyze the question
            Action: ChartSelector
            Action Input: "{question}"
            Observation: [chart-type]
            Thought: Now generate code
            Action: CodeGenerator
            Action Input: "{question}|[chart-type]"
            FINAL ANSWER:"""
        })
        return result['output']