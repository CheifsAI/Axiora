import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from OprFuncs import *
from langchain_core.runnables import RunnableSequence
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, Tool, create_react_agent
from langchain import hub
import re
from DatabaseManager import DatabaseManager
from datetime import datetime

class DataAnalyzer:
    def __init__(self,dataframe,llm):
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_summary = data_describer(dataframe)
        self.data_sample = dataframe.head().to_string()
        self.data_cols = ", ".join(dataframe.columns)
        self.db = DatabaseManager()
        self.report_id = None
        self.memory = []
        self.rname = "output"
        os.makedirs(self.rname, exist_ok=True)

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
        self.db.saveMemory(reportID=self.report_id,
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
            self.db.saveMemory(reportID=self.report_id,
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
        self.db.saveMemory(reportID=self.report_id,
                           llm=self.db.llm_id_by_name(self.llm.model),
                           prompet=question,
                           response=response,
                           chat=True)

        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response))
        return response
    

    def _chart_select_chain(self, question):
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
    | Comparing two related metrics      | Bar (grouped)   | Compare pairs of values side by side    |
    | Time series analysis               | Line            | Track trends over time (years, months)  |
    | Comparing >3 categories            | Bar             | Compare discrete values across groups   |
    | Distribution of data               | Histogram       | Show frequency distribution of data     |
    | Comparing 2-5 categories           | Pie             | Show proportions (limit to 5 categories)|
    | Part-to-whole relationships        | StackedBar      | Show cumulative totals and components  |
    | Multivariate comparison            | Radar           | Compare multiple quantitative variables |
    | Statistical distribution analysis  | Box             | Show quartiles and outliers            |"""

        # Special handling for comparison questions
        if "compare" in question.lower() or "vs" in question.lower() or "versus" in question.lower():
            if "goal" in question.lower() and "Home Team Goals" in self.dataframe.columns:
                return {
                    "chart_type": "Bar",
                    "chart_title": "Goals_Comparison",
                    "columns": "Home Team Goals"  # This will trigger the special comparison logic
                }

        prompt = PromptTemplate(
            input_variables=["data_cols", "guidelines", "question"],
            template="""You are a data visualization expert. Based on the available columns and guidelines, select the most appropriate visualization type and column for the given question.
            
Available columns: {data_cols}

Chart selection guidelines:
{guidelines}

Question: {question}

Respond in this exact format (no other text):
chart_type: [type]
column: [single column name]

The column MUST be one of the available columns listed above.
The chart_type should be one of: bar, line, pie, histogram, stackedbar, radar, box

For questions about frequencies, distributions, or "most common" values, use Bar or Pie charts.
For comparison questions between two metrics, use Bar with the primary metric."""
        )

        chain = prompt | llm

        result = chain.invoke({
            "data_cols": data_cols,
            "guidelines": guidelines,
            "question": question
        })

        # Parse the response
        chart_type = None
        column = None
        
        # Handle both string and AIMessage responses
        response_text = result if isinstance(result, str) else result.content
        print("Raw LLM response:", response_text)
        
        for line in response_text.split('\n'):
            line = line.strip().lower()
            if line.startswith('chart_type:'):
                chart_type = line.split(':')[1].strip()
            elif line.startswith('column:'):
                # Get the column name and find the exact match in dataframe columns
                col_name = line.split(':')[1].strip()
                # Try to find an exact match first
                for df_col in self.dataframe.columns:
                    if df_col.lower() == col_name.lower():
                        column = df_col
                        break
                # If no exact match, try partial match
                if not column:
                    for df_col in self.dataframe.columns:
                        if col_name.lower() in df_col.lower():
                            column = df_col
                            break
        
        # Validate and clean up
        if not chart_type or not column:
            print("Warning: Could not parse chart type or column from response. Using defaults.")
            print("Response was:", response_text)
            print("Available columns:", self.data_cols)
            
            # Try to find a relevant column based on the question
            question_lower = question.lower()
            if "goal" in question_lower:
                column = "Home Team Goals"  # This will trigger the special comparison logic
                chart_type = "Bar"
            else:
                column = self.dataframe.columns[0]
                chart_type = "Bar"
            
        chart_type = chart_type_mapping.get(chart_type, "Bar")
        
        # Verify column exists in dataframe
        if column not in self.dataframe.columns:
            print(f"Warning: Column '{column}' not found. Available columns: {self.data_cols}")
            column = self.dataframe.columns[0]
        
        # Create descriptive title
        if "goal" in question.lower():
            title = "Goals_Analysis"
        else:
            title = f"{column}_Analysis"
            
        return {
            "chart_type": chart_type,
            "chart_title": title,
            "columns": column
        }

    def visual(self, chart_type, column_name, data):
        """Generate a visualization based on the specified chart type and data."""
        try:
            # Convert data to DataFrame if it's not already
            df = pd.DataFrame(data) if not isinstance(data, pd.DataFrame) else data
            
            # Create a unique filename for the chart
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_column_name = "".join(c if c.isalnum() else "_" for c in column_name)
            filename = f"{chart_type}_{safe_column_name}_{timestamp}.html"
            
            # Ensure output directory exists
            os.makedirs(self.rname, exist_ok=True)
            output_path = os.path.join(self.rname, filename)
            print(f"Generating chart at: {output_path}")
            
            # Special handling for goal comparison
            if "goal" in column_name.lower():
                home_goals = df["Home Team Goals"] if "Home Team Goals" in df.columns else None
                away_goals = df["Away Team Goals"] if "Away Team Goals" in df.columns else None
                
                if home_goals is not None and away_goals is not None:
                    # Create comparison bar chart
                    fig = go.Figure()
                    
                    # Add home goals
                    fig.add_trace(go.Bar(
                        name='Home Team Goals',
                        x=df.index,
                        y=home_goals,
                        text=[f"{v:,}" if pd.notna(v) else "N/A" for v in home_goals],
                        textposition='auto',
                    ))
                    
                    # Add away goals
                    fig.add_trace(go.Bar(
                        name='Away Team Goals',
                        x=df.index,
                        y=away_goals,
                        text=[f"{v:,}" if pd.notna(v) else "N/A" for v in away_goals],
                        textposition='auto',
                    ))
                    
                    # Update layout
                    fig.update_layout(
                        title='Comparison of Home vs Away Team Goals',
                        xaxis_title='Match Index',
                        yaxis_title='Goals Scored',
                        barmode='group',
                        template='plotly_white'
                    )
                    
                    fig.write_html(output_path)
                    print(f"Successfully generated comparison chart at {output_path}")
                    return output_path
            
            # If not a goal comparison or missing columns, fall back to regular chart
            values = df[column_name].replace({np.nan: None})
            
            # Define chart templates
            chart_templates = {
                'Bar': f"""
fig = go.Figure(data=[
    go.Bar(
        x=[str(x) for x in df.index],
        y=[v if v is not None else 0 for v in values],
        text=[str(v) if v is not None else "N/A" for v in values],
        textposition='auto',
    )
])
fig.update_layout(
    title=f'Bar Chart of {column_name}',
    xaxis_title='Index',
    yaxis_title=f'{column_name}',
    template='plotly_white'
)
""",
                'Pie': f"""
fig = go.Figure(data=[
    go.Pie(
        labels=[str(x) for x in df.index],
        values=[v if v is not None else 0 for v in values],
        textinfo='label+percent',
        hovertemplate="%{{label}}<br>Value: %{{value}}<extra></extra>"
    )
])
fig.update_layout(
    title=f'Pie Chart of {column_name}',
    template='plotly_white'
)
""",
                'Histogram': f"""
fig = go.Figure(data=[
    go.Histogram(
        x=[v for v in values if v is not None],
        nbinsx=30,
        name='{column_name}'
    )
])
fig.update_layout(
    title=f'Histogram of {column_name}',
    xaxis_title=f'{column_name}',
    yaxis_title='Count',
    template='plotly_white'
)
""",
                'Box': f"""
fig = go.Figure(data=[
    go.Box(
        y=[v for v in values if v is not None],
        name='{column_name}',
        boxpoints='all',
        jitter=0.3,
        pointpos=-1.8
    )
])
fig.update_layout(
    title=f'Box Plot of {column_name}',
    yaxis_title=f'{column_name}',
    template='plotly_white'
)
"""
            }
            
            # Get the appropriate template or default to Bar
            code = chart_templates.get(chart_type, chart_templates['Bar'])
            
            # Create a clean environment for executing the code
            exec_env = {
                'go': go,
                'df': df,
                'values': values,
                'np': np
            }
            
            # Execute the chart generation code
            try:
                exec(code, exec_env)
                fig = exec_env['fig']
                fig.write_html(output_path)
                print(f"Successfully generated chart at {output_path}")
                return output_path
            except Exception as e:
                raise Exception(f"Error generating chart: {str(e)}")
                
        except Exception as e:
            raise Exception(f"❌ Error generating chart: {str(e)}")