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
            
            # Font configurations
            font_config = {
                'family': 'Segoe UI',
                'title_size': 20,      # Slightly smaller title
                'axis_title_size': 14, # Smaller axis titles
                'tick_size': 12,       # Smaller tick labels
                'legend_size': 12,     # Smaller legend
                'label_size': 10       # Smaller data labels
            }
            
            # Define theme colors with blue and green data colors but dark background
            theme_colors = {
                'primary': '#2196F3',      # Bright blue
                'secondary': '#4CAF50',    # Green
                'accent': '#1976D2',       # Darker blue
                'accent2': '#388E3C',      # Darker green
                'accent3': '#64B5F6',      # Light blue
                'accent4': '#81C784',      # Light green
                'accent5': '#0D47A1',      # Navy blue
                'background': '#708090 ',   # Dark background
                'text': '#E0E0E0',         # Light gray text
                'grid': '#1F2937'          # Dark grid lines
            }
            
            # Custom theme for plotly
            custom_theme = {
                'layout': {
                    'plot_bgcolor': theme_colors['background'],
                    'paper_bgcolor': theme_colors['background'],
                    'width': 1200,
                    'height': 800,
                    'font': {
                        'family': font_config['family'],
                        'color': theme_colors['text'],
                        'size': font_config['label_size']
                    },
                    'title': {
                        'font': {
                            'color': theme_colors['text'],
                            'size': font_config['title_size'],
                            'family': font_config['family']
                        }
                    },
                    'showlegend': True,
                    'legend': {
                        'bgcolor': 'rgba(17, 24, 39, 0.8)',  # Semi-transparent dark background
                        'font': {'color': theme_colors['text']},
                        'bordercolor': theme_colors['grid'],
                        'borderwidth': 1
                    },
                    'colorway': [
                        theme_colors['primary'],    # Bright blue
                        theme_colors['secondary'],  # Green
                        theme_colors['accent3'],    # Light blue
                        theme_colors['accent4'],    # Light green
                        theme_colors['accent'],     # Darker blue
                        theme_colors['accent2'],    # Darker green
                        theme_colors['accent5'],    # Navy blue
                    ],
                    'xaxis': {
                        'gridcolor': theme_colors['grid'],
                        'linecolor': theme_colors['grid'],
                        'tickcolor': theme_colors['text'],
                        'tickfont': {'color': theme_colors['text']},
                        'title': {'font': {'color': theme_colors['text']}}
                    },
                    'yaxis': {
                        'gridcolor': theme_colors['grid'],
                        'linecolor': theme_colors['grid'],
                        'tickcolor': theme_colors['text'],
                        'tickfont': {'color': theme_colors['text']},
                        'title': {'font': {'color': theme_colors['text']}}
                    }
                }
            }
            
            # Ensure output directory exists
            os.makedirs(self.rname, exist_ok=True)
            output_path = os.path.join(self.rname, filename)
            print(f"Generating chart at: {output_path}")
            
            # Special handling for goal comparison
            if "goal" in column_name.lower():
                home_goals = df["Home Team Goals"] if "Home Team Goals" in df.columns else None
                away_goals = df["Away Team Goals"] if "Away Team Goals" in df.columns else None
                
                if home_goals is not None and away_goals is not None:
                    # Create comparison bar chart with blue and green colors
                    fig = go.Figure()
                    
                    # Add home goals with blue theme
                    fig.add_trace(go.Bar(
                        name='Home Team Goals',
                        x=df.index,
                        y=home_goals,
                        text=[f"{v:,}" if pd.notna(v) else "N/A" for v in home_goals],
                        textposition='auto',
                        marker=dict(
                            color='#2196F3',  # Bright blue
                            line=dict(
                                color='#1976D2',  # Darker blue
                                width=1.5
                            )
                        ),
                        opacity=0.9
                    ))
                    
                    # Add away goals with green theme
                    fig.add_trace(go.Bar(
                        name='Away Team Goals',
                        x=df.index,
                        y=away_goals,
                        text=[f"{v:,}" if pd.notna(v) else "N/A" for v in away_goals],
                        textposition='auto',
                        marker=dict(
                            color='#4CAF50',  # Green
                            line=dict(
                                color='#388E3C',  # Darker green
                                width=1.5
                            )
                        ),
                        opacity=0.9
                    ))
                    
                    # Create layout configuration with enhanced styling
                    layout = {
                        **custom_theme['layout'],
                        'title': {
                            'text': 'Comparison of Home vs Away Team Goals',
                            'font': {
                                'size': font_config['title_size'],
                                'color': theme_colors['text'],
                                'family': font_config['family']
                            },
                            'x': 0.5,
                            'xanchor': 'center',
                            'y': 0.95,
                            'yanchor': 'top'
                        },
                        'xaxis_title': 'Match Index',
                        'yaxis_title': 'Goals Scored',
                        'barmode': 'group',
                        'bargap': 0.15,        # Gap between bars
                        'bargroupgap': 0.1,    # Gap between bar groups
                        'showlegend': True,
                        'legend': {
                            'bgcolor': 'rgba(26, 35, 126, 0.8)',
                            'bordercolor': theme_colors['grid'],
                            'borderwidth': 1,
                            'font': {
                                'family': font_config['family'],
                                'size': font_config['legend_size'],
                                'color': theme_colors['text']
                            }
                        },
                        'hoverlabel': {
                            'bgcolor': theme_colors['background'],
                            'bordercolor': theme_colors['grid'],
                            'font': {
                                'family': font_config['family'],
                                'size': font_config['label_size'],
                                'color': theme_colors['text']
                            }
                        }
                    }
                    
                    # Update layout
                    fig.update_layout(**layout)
                    
                    # Update axes for better readability
                    fig.update_xaxes(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor=theme_colors['grid'],
                        zeroline=False
                    )
                    
                    fig.update_yaxes(
                        showgrid=True,
                        gridwidth=1,
                        gridcolor=theme_colors['grid'],
                        zeroline=False
                    )
                    
                    fig.write_html(output_path)
                    print(f"Successfully generated comparison chart at {output_path}")
                    return output_path
            
            # If not a goal comparison or missing columns, fall back to regular chart
            values = df[column_name].replace({np.nan: None})
            
            # Update the chart templates with new colors and sizing
            chart_templates = {
                'Bar': f"""
fig = go.Figure(data=[
    go.Bar(
        x=[str(x) for x in df.index],
        y=[v if v is not None else 0 for v in values],
        text=[str(v) if v is not None else "N/A" for v in values],
        textposition='auto',
        marker_color='{theme_colors["primary"]}',
        marker_line_color='{theme_colors["grid"]}',
        marker_line_width=1,
        textfont={{
            'color': '{theme_colors["text"]}',
            'size': {font_config['label_size']},
            'family': '{font_config["family"]}'
        }},
        hoverinfo='y+text',
        hoverlabel={{
            'bgcolor': '{theme_colors["background"]}',
            'bordercolor': '{theme_colors["grid"]}',
            'font': {{
                'size': {font_config['label_size']},
                'family': '{font_config["family"]}'
            }}
        }}
    )
])

layout = {{
    **custom_theme['layout'],
    'title': {{
        'text': f'Analysis of {column_name}',
        'font': {{
            'size': {font_config['title_size']},
            'color': '{theme_colors["text"]}',
            'family': '{font_config["family"]}'
        }},
        'x': 0.5,
        'xanchor': 'center',
        'y': 0.95,
        'yanchor': 'top'
    }},
    'xaxis_title': 'Index',
    'yaxis_title': f'{column_name}'
}}

fig.update_layout(**layout)
""",
                'Pie': f"""
fig = go.Figure(data=[
    go.Pie(
        labels=[str(x) for x in df.index],
        values=[v if v is not None else 0 for v in values],
        textinfo='percent+label',
        textposition='auto',
        hoverinfo='label+value+percent',
        marker=dict(
            colors=['{theme_colors["primary"]}', '{theme_colors["secondary"]}', '{theme_colors["accent"]}'],
            line=dict(color='{theme_colors["grid"]}', width=2)
        ),
        textfont={{
            'color': '{theme_colors["text"]}',
            'size': {font_config['label_size']},
            'family': '{font_config["family"]}'
        }},
        hoverlabel={{
            'bgcolor': '{theme_colors["background"]}',
            'bordercolor': '{theme_colors["grid"]}',
            'font': {{
                'size': {font_config['label_size']},
                'family': '{font_config["family"]}'
            }}
        }}
    )
])

layout = {{
    **custom_theme['layout'],
    'title': {{
        'text': f'Distribution of {column_name}',
        'font': {{
            'size': {font_config['title_size']},
            'color': '{theme_colors["text"]}',
            'family': '{font_config["family"]}'
        }},
        'x': 0.5,
        'xanchor': 'center',
        'y': 0.95,
        'yanchor': 'top'
    }}
}}

fig.update_layout(**layout)
""",
                'Histogram': f"""
fig = go.Figure(data=[
    go.Histogram(
        x=[v for v in values if v is not None],
        nbinsx=30,
        name='{column_name}',
        marker_color='{theme_colors["primary"]}',
        marker_line_color='{theme_colors["grid"]}',
        marker_line_width=1,
        opacity=0.8,
        textfont={{
            'color': '{theme_colors["text"]}',
            'size': {font_config['label_size']},
            'family': '{font_config["family"]}'
        }},
        hoverlabel={{
            'bgcolor': '{theme_colors["background"]}',
            'bordercolor': '{theme_colors["grid"]}',
            'font': {{
                'size': {font_config['label_size']},
                'family': '{font_config["family"]}'
            }}
        }}
    )
])

layout = {{
    **custom_theme['layout'],
    'title': {{
        'text': f'Frequency Distribution of {column_name}',
        'font': {{
            'size': {font_config['title_size']},
            'color': '{theme_colors["text"]}',
            'family': '{font_config["family"]}'
        }},
        'x': 0.5,
        'xanchor': 'center',
        'y': 0.95,
        'yanchor': 'top'
    }},
    'xaxis_title': f'{column_name}',
    'yaxis_title': 'Count'
}}

fig.update_layout(**layout)
""",
                'Box': f"""
fig = go.Figure(data=[
    go.Box(
        y=[v for v in values if v is not None],
        name='{column_name}',
        boxpoints='outliers',
        jitter=0.3,
        pointpos=-1.8,
        marker_color='{theme_colors["primary"]}',
        line_color='{theme_colors["secondary"]}',
        fillcolor='{theme_colors["primary"]}',
        marker=dict(
            color='{theme_colors["accent"]}',
            size=6,
            line=dict(color='{theme_colors["grid"]}', width=1)
        ),
        hoverlabel=dict(
            font=dict(
                size={font_config['label_size']},
                family='{font_config["family"]}'
            ),
            bgcolor='{theme_colors["background"]}',
            bordercolor='{theme_colors["grid"]}'
        )
    )
])

layout = {{
    **custom_theme['layout'],
    'title': {{
        'text': f'Distribution Analysis of {column_name}',
        'font': {{
            'size': {font_config['title_size']},
            'color': '{theme_colors["text"]}',
            'family': '{font_config["family"]}'
        }},
        'x': 0.5,
        'xanchor': 'center',
        'y': 0.95,
        'yanchor': 'top'
    }},
    'yaxis_title': f'{column_name}'
}}

fig.update_layout(**layout)
"""
            }
            
            # Get the appropriate template or default to Bar
            code = chart_templates.get(chart_type, chart_templates['Bar'])
            
            # Create a clean environment for executing the code
            exec_env = {
                'go': go,
                'df': df,
                'values': values,
                'np': np,
                'custom_theme': custom_theme
            }
            
            # Execute the chart generation code
            try:
                exec(code, exec_env)
                fig = exec_env['fig']
                
                # Add common layout updates for interactivity
                fig.update_layout(
                    hovermode='x unified',
                    hoverlabel=dict(
                        bgcolor=theme_colors['secondary'],
                        font_size=14,
                        font_family="Segoe UI"
                    ),
                    modebar=dict(
                        bgcolor='rgba(0,0,0,0)',
                        color=theme_colors['primary'],
                        activecolor=theme_colors['secondary']
                    )
                )
                
                fig.write_html(output_path)
                print(f"Successfully generated chart at {output_path}")

                # Update the chart load finished handler
                js = """
                if (window.Plotly) {
                    var gd = document.querySelector('.plotly-graph-div');
                    if (gd) {
                        Plotly.relayout(gd, {
                            'showlink': false,
                            'modeBarButtonsToRemove': ['sendDataToCloud'],
                            'responsive': true,
                            'displayModeBar': true,
                            'scrollZoom': true,
                            'editable': true,
                            'dragmode': 'zoom',
                            'hoverlabel': {
                                'font': {
                                    'size': 14,
                                    'family': 'Segoe UI'
                                }
                            }
                        });
                        
                        // Enable single-click interactions
                        gd.on('plotly_click', function(data) {
                            var point = data.points[0];
                            console.log('Clicked point:', point);
                        });
                        
                        // Make chart responsive
                        window.addEventListener('resize', function() {
                            Plotly.Plots.resize(gd);
                        });
                    }
                }
                """
                return output_path
            except Exception as e:
                raise Exception(f"Error generating chart: {str(e)}")
                
        except Exception as e:
            raise Exception(f"❌ Error generating chart: {str(e)}")