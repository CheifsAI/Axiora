import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Union, Any
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from OprFuncs import *
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import re
from DatabaseManager import DatabaseManager
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def ensure_string(content: Any) -> str:
    """
    Ensure the content is a string, extracting content from AIMessage if needed.
    
    Parameters:
        content: Content that might be a string, AIMessage, or other object
        
    Returns:
        str: The string content
    """
    if isinstance(content, AIMessage):
        return str(content.content)
    elif hasattr(content, 'content'):
        return str(content.content)
    return str(content)

class DataAnalyzer:
    """
    A class for data analysis using Large Language Models (LLMs).
    
    This class provides a comprehensive interface for data analysis,
    generating recommendations, and creating visualizations using large language models.
    
    Attributes:
        dataframe (pd.DataFrame): The dataframe being analyzed
        llm: The large language model used for analysis
        data_info (str): Automatically inferred information about the data
        data_description (str): Description of the data
        data_sample (str): Sample of the data (first rows)
        data_cols (str): List of column names separated by commas
        
    Examples:
        >>> from DataAnalyzer import DataAnalyzer
        >>> import pandas as pd
        >>> from langchain_openai import ChatOpenAI
        >>> 
        >>> # Create a new instance
        >>> df = pd.read_csv("data.csv")
        >>> llm = ChatOpenAI()
        >>> analyzer = DataAnalyzer(df, llm)
        >>> 
        >>> # Analyze the data
        >>> analysis = analyzer.analysis_data()
        >>> 
        >>> # Generate questions and recommendations
        >>> questions = analyzer.questions_gen(5)
        >>> recommendations = analyzer.generate_recommendations()
    """
    def __init__(self, dataframe, llm, user_id=None):
        """
        Initialize the data analyzer with a dataframe and a large language model.
        
        Parameters:
            dataframe (pd.DataFrame): The dataframe to analyze
            llm: The large language model to use for analysis
            user_id (str, optional): User ID for tracking analytics. Default is None.
            
        Example:
            >>> analyzer = DataAnalyzer(df, llm, user_id="user123")
        """
        self.dataframe = dataframe
        self.llm = llm
        self.data_info = data_infer(dataframe)
        self.data_description = data_describer(dataframe)
        self.data_sample = dataframe.head().to_string()
        self.data_cols = ", ".join(dataframe.columns)
        self.db = DatabaseManager()
        self.report_id = None
        self.memory = []
        self.user_id = user_id
        
    def analysis_data(self):
        """
        Analyze the data using the large language model to create a comprehensive analytical report.
        
        This function sends data information to the large language model to create
        a deep analysis including executive summary, key patterns, statistical validation,
        risks, growth opportunities, and strategic recommendations.
        
        Returns:
            str: The text analysis report
            
        Notes:
            - The analysis result is stored in self.analysis.
            - The conversation history is stored in self.memory.
            - The analysis is saved to the database if self.report_id is set.
            
        Example:
            >>> analysis_report = analyzer.analysis_data()
            >>> print(analysis_report[:500])  # Display just the beginning as the report may be long
        """
        data_info = self.data_info
        data_sample = self.data_sample
        data_description = self.data_description

        analysis_template = '''
        You are a data analyst. You are provided with:
        1. Dataset metadata: {data_info}
        2. Dataset sample: {data_sample}
        3. Dataset summary: {data_description}
        You are a **world-class Senior Data Analyst and Applied Statistician**, with deep expertise in business intelligence, behavioral data, financial analytics, and statistical modeling. I will provide you with a dataset in the form of a DataFrame, CSV, or Excel file.

        🎯 Your task is to perform a **comprehensive, statistically-sound, and executive-ready analysis** tailored for decision-makers, technical stakeholders, and strategic planners.

        ---

        ## 🧾 1. Executive Summary
        - Summarize the most important findings, using clear and impactful language.
        - Highlight how these findings affect the business, strategy, or operations.
        - Include headline numbers (KPIs, revenue impact, user behavior shifts...).

        ---

        ## 📊 2. Key Patterns & Strategic Insights
        - Explore key trends, distributions, and variable relationships.
        - Use metrics such as:
        - **Mean, Median, Std. Dev.**
        - **Correlation Coefficients**
        - **Distribution Skewness/Kurtosis**
        - **R² Score (if regression applies)**

        📌 Visuals may include histograms, bar charts, scatter plots, or heatmaps.

        ---

        ## 📐 3. Statistical Validation & Modeling
        - Apply formal **hypothesis tests** where applicable:
        - t-tests, ANOVA, Chi-square, or Z-tests.
        - Report **p-values** and **statistical significance**.
        - Build simple predictive or explanatory models:
        - Linear/Logistic Regression, Decision Trees...
        - Report key metrics:
        - **R²**, **RMSE**, **AUC**, or **F1-Score** (as appropriate).
        - Provide **Confidence Intervals** for estimates when relevant.

        📈 Clearly indicate statistically significant results and what they mean for the business.

        ---

        ## ⚠️ 4. Risks, Anomalies & Data Limitations
        - Identify:
        - Missing values
        - Outliers
        - Sampling bias or measurement error
        - Explain how each issue might impact model validity or business interpretations.
        - Suggest methods for mitigation (e.g., imputation, resampling, anomaly filtering).

        ---

        ## 🌱 5. Opportunities for Growth & Optimization
        - Identify actionable insights tied to business KPIs.
        - Use segmentation, clustering, or cross-tab analysis to discover growth potential.
        - Prioritize by impact, feasibility, and risk.

        ---

        ## 💡 6. Hidden or Surprising Insights
        - Detect any **non-obvious** trends, patterns, or behaviors.
        - Show how these findings might reveal blind spots or strategic advantages.

        ---

        ## 🧠 7. Strategic Recommendations
        - Provide **3–5 clear, data-backed actions** for decision-makers.
        - Align each with business objectives (cost savings, revenue growth, efficiency).
        - Include a "next steps" section (further data needed, A/B test, dashboard build...).

        ---

        ## 📊 Summary Table of Key Drivers

        | Category              | Factor            | Impact Level | Statistical Significance | Recommendation                      |
        |----------------------|-------------------|--------------|---------------------------|-------------------------------------|
        | 📈 High Impact       | [Variable Name]   | Strong       | ✅ p < 0.05                | [Recommended Action]               |
        | ⚠️ Low/Negative Impact | [Variable Name]   | Weak/Negative| ❌ Not significant         | [Mitigation Strategy or Ignore]    |

        ---

        ## 📌 Presentation Guidelines
        - Use professional, business-oriented language.
        - Include emojis 🎯 📈 ⚠️ 💡 💰 🔍 to enhance readability.
        - Be clear, direct, and data-driven.
        - If any part of the dataset is unclear or incomplete, ask clarifying questions before finalizing.

        Once the dataset is received, begin your advanced analysis.
        '''

        analysis_prompt = PromptTemplate(
            input_variables=["data_info", "data_sample", "data_description"],
            template=analysis_template
        )
        
        analysis_chain = analysis_prompt | self.llm

        self.analysis = analysis_chain.invoke({
            "data_info": data_info,
            "data_sample": data_sample,
            "data_description": data_description
        })

        # Ensure the analysis is a string
        analysis_str = ensure_string(self.analysis)
        self.analysis = analysis_str

        formatted_analysis_prompt = analysis_template.format(
            data_info=data_info,
            data_sample=data_sample,
            data_description=data_description
        )
        self.memory.append(HumanMessage(content=formatted_analysis_prompt))
        self.memory.append(AIMessage(content=analysis_str))
        self.db.saveMemory(
            reportID=self.report_id,
            llm=self.db.llm_id_by_name(self.llm.model),
            prompet=formatted_analysis_prompt,
            response=analysis_str,
            chat=False
        )
        return self.analysis        

    def questions_gen(self, num):
        """
        Generate strategic analytical questions that can be visualized based on the data.
        
        This function uses the large language model to generate high business value questions
        that can be used to explore the data or create dashboards.
        
        Parameters:
            num (int): Number of questions to generate
            
        Returns:
            List[str]: List of generated analytical questions
            
        Notes:
            - Generated questions focus on trends, patterns, and relationships in the data.
            - Questions are stored in the conversation history (self.memory).
            - Questions are saved to the database if self.report_id is set.
            
        Example:
            >>> questions = analyzer.questions_gen(5)
            >>> for i, q in enumerate(questions, 1):
            ...     print(f"{i}. {q}")
            1. How has the sales rate evolved over the past 12 months?
            2. What are the top 5 best-selling products and what is their contribution to total sales?
            3. What is the distribution of customers by geographic region?
            4. Is there a relationship between order volume and complaint rate?
            5. Which marketing channels are most effective in terms of conversion rate?
        """
        data_info = self.data_info
        data_sample = self.data_sample
        data_description = self.data_description
        

        question_prompt = f"""
        You are a senior data analyst hired by a company to extract meaningful, high-level, and actionable business insights from the following dataset.

        Your job is to generate advanced **strategic questions** that:
        - Are deeply rooted in the data structure and semantics.
        - Reflect important **business objectives**, patterns, risks, or growth opportunities.
        - Are **strong, insightful, and relevant** to decision-makers like company owners or managers.
        - Can be **easily visualized** using bar charts, line plots, histograms, scatter plots, or pie charts.

        **DO NOT generate general or surface-level questions. Instead, focus on questions that:**
        - Quantify change over time or between groups.
        - Explore distribution, frequency, or correlation.
        - Investigate trends, seasonality, or anomalies.
        - Provide guidance for optimizing business performance or identifying risks.

        You MUST generate exactly {num} chartable, insightful questions.

        ### INPUTS:
        1. Dataset Overview: {data_info}
        2. Dataset Sample: {data_sample}
        3. Data Summary: {data_description}

        ### OUTPUT FORMAT:
        Write {num} powerful analytical questions that:
        - Could be visualized with a chart.
        - Have clear business relevance.
        - Reflect advanced reasoning.

        Each question should be written on a separate line.

        Example Questions:
        - How has the conversion rate changed over time across different marketing channels?
        - Which regions have shown the fastest growth in revenue over the past year?
        - What is the correlation between customer satisfaction scores and return frequency?
        - How does the average transaction value vary by customer segment?
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

            # Ensure the response is a string
            generated_questions = ensure_string(generated_questions)

            # Ensure the response is properly encoded
            if isinstance(generated_questions, str):
                generated_questions = generated_questions.encode('utf-8', 'replace').decode('utf-8')

            if not generated_questions.strip():
                logger.warning("LLM did not generate any questions.")
                return []

            # Use the improved extraction function
            questions_list = extract_questions(generated_questions)

            # Trim or handle missing questions
            if len(questions_list) > num:
                questions_list = questions_list[:num]
            elif len(questions_list) < num:
                logger.warning(f"Expected {num} questions, but got {len(questions_list)}")

            # Store in memory
            formatted_question_prompt = question_template.format(
                num=num,
                data_info=data_info,
                data_sample=data_sample,
                data_description=data_description
            )
            self.memory.append(HumanMessage(content=formatted_question_prompt))
            self.memory.append(AIMessage(content="\n".join(questions_list)))
            self.db.saveMemory(
                reportID=self.report_id,
                llm=self.db.llm_id_by_name(self.llm.model),
                prompet=formatted_question_prompt,
                response="\n".join(questions_list),
                chat=False
            )

            return questions_list

        except Exception as e:
            logger.error(f"Error generating questions: {str(e)}")
            return []
    
    def chat(self, question: str) -> str:
        """
        Interact with the data analysis system to answer questions about the dataset.
        
        This function uses the large language model with previous conversation history
        to provide accurate and contextual answers about the data.
        
        Parameters:
            question (str): User's question about the data
            
        Returns:
            str: The model's response with data-informed insights
            
        Notes:
            - The question and answer are stored in the conversation history (self.memory).
            - The conversation is saved to the database if self.report_id is set.
            - The model can leverage all previous analyses in the answer.
            
        Example:
            >>> response = analyzer.chat("Which product category has the highest sales?")
            >>> print(response)
            Based on the data, the "Electronics" category has the highest sales with 37% of total sales,
            followed by "Home Appliances" with 24%.
        """
        system_prompt = f"""
        You are an expert data analyst with deep expertise in {self.dataframe.shape[1]} variables across {self.dataframe.shape[0]} records.

        Dataset context:
        - Type of data: {self.data_info.splitlines()[0] if self.data_info else 'Unknown dataset'}
        - Key columns: {', '.join(self.dataframe.columns[:5]) if len(self.dataframe.columns) > 5 else self.data_cols}
        - Total records: {self.dataframe.shape[0]:,}

        Instructions:
        - Answer using ONLY the data available
        - Support responses in multiple languages when requested
        - If asked about unknown variables, respond transparently
        - Include relevant statistics and numerical evidence when applicable
        - Format responses with clear structure: summary first, then details
        - Prioritize insights that lead to actionable business decisions
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}")
        ])

        chain = prompt | self.llm

        response = chain.invoke({
            "chat_history": self.memory,
            "question": question
        })
        
        # Ensure response is a string
        response_str = ensure_string(response)

        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response_str))

        self.db.saveMemory(
            reportID=self.report_id,
            llm=self.db.llm_id_by_name(self.llm.model),
            prompet=question,
            response=response_str,
            chat=True
        )

        return response_str
    
    def select_chart_type(self, question: str) -> str:
        """
        Select the appropriate chart type based on the question and data.
        
        This function analyzes the question and determines the most suitable chart type
        for visualizing the answer.
        
        Parameters:
            question (str): The analytical question to visualize
            
        Returns:
            str: The appropriate chart type ('Bar', 'Line', 'Pie', 'Scatter', 'Histogram')
            
        Notes:
            - Bar: Used for comparing categories
            - Line: Used for trends over time
            - Pie: Used for parts of a whole (with few categories)
            - Scatter: Used for relationships
            - Histogram: Used for distribution of numerical variables
        """
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
        allowed_charts = {
            'Bar', 'Line', 'Histogram', 
            'Pie', 'Scatter'
        }
        return chart_type if chart_type in allowed_charts else 'Bar'
    
    def select_columns(self, question: str) -> List[str]:
        """
        Select the relevant columns based on the question and data.
        
        This function analyzes the question and determines the most appropriate columns
        to use for the analysis.
        
        Parameters:
            question (str): The analytical question
            
        Returns:
            List[str]: List of relevant column names
            
        Notes:
            - Focuses on columns mentioned in the question
            - Determines what is being measured (numerical columns)
            - Determines what is being compared/grouped by (categorical columns)
            - Identifies any time dimensions for trends
        """
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

        self.llm.temperature = 0.3
        chain = self.columns_prompt | self.llm
        response = chain.invoke({
            "data_description": self.data_description,
            "columns": self.data_cols,
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
        """
        Get a comprehensive chart recommendation (type and columns) based on a question.
        
        This function combines select_chart_type and select_columns to get a complete
        visualization recommendation.
        
        Parameters:
            question (str): The analytical question to visualize
            
        Returns:
            Tuple[str, List[str]]: A pair of chart type and list of relevant columns
        """
        chart_type = self.select_chart_type(question)
        columns = self.select_columns(question)
        return chart_type, columns
    
    def generate_recommendations(self, num_recommendations: int = 5):
        """
        Generate strategic business recommendations based on data analysis.
        
        This function uses the large language model with previous data analysis to create
        actionable recommendations with business impact.
        
        Parameters:
            num_recommendations (int, optional): Number of recommendations to generate. Default is 5.
            
        Returns:
            str: Text containing recommendations organized in a table and with full details
            
        Notes:
            - Recommendations are based on analysis results (self.analysis).
            - Recommendations include title, details, expected impact, and potential risks.
            - Risks are categorized with emojis: ✅ (low), ⚠️ (medium), ❗(high).
            - Recommendations are stored in the conversation history (self.memory).
            - Recommendations are saved to the database if self.report_id is set.
        """
        data_info = self.data_info
        data_sample = self.data_sample
        data_description = self.data_description
        analysis = self.analysis

        recommendation_prompt = '''
        You are a world-class business consultant and data analyst.

        You have analyzed the following:
        - Dataset metadata: {data_info}
        - Dataset sample: {data_sample}
        - Dataset summary: {data_description}
        - Detailed business analysis: {analysis}

        Based on your deep understanding of the data and analysis:
        Your task is to generate {num_recommendations} highly actionable, strategic recommendations for the business.

        Your recommendations must:
        - Be directly based on the analysis and insights.
        - Address clear business actions (e.g., optimize processes, launch new products, reduce risks, target specific segments, etc.)
        - Be specific, impactful, and feasible.
        - Cover both short-term quick wins and long-term strategic moves.
        - Include estimated expected outcome in percentage (%) where appropriate.
        - Include any potential risks or challenges for each recommendation.
        - Reference relevant metrics or insights from the analysis if possible.
        - Use professional, executive-level language.
        - Add an appropriate emoji based on risk level:
            - ✅ for Low risk
            - ⚠️ for Medium risk
            - ❗for High risk

        Output Format:

        ### 📋 Recommendations Table

        | # | Recommendation Title | Expected Impact (%) | Potential Risk (with Emoji) |
        |---|-----------------------|---------------------|-----------------------------|
        | 1 | [Title] | [Estimated Impact %] | [Emoji] [Main risk] |
        | 2 | [Title] | [Estimated Impact %] | [Emoji] [Main risk] |
        | ... | ... | ... | ... |

        ---

        ### 📋 Full Recommendation Details

        1. **[Recommendation Title]** [Emoji]
        - **Details:** Explain clearly what should be done and why.
        - **Expected Impact:** [e.g., Increase attendance by 10%]
        - **Metrics Reference:** [Reference specific metric if available, e.g., matches with <50% attendance]
        - **Potential Risks:** [Possible challenges or risks involved]
        - **Timeline:** [Short-term or Long-term]

        Repeat similarly for each recommendation.
        '''

        rec_template = PromptTemplate(
            input_variables=["data_info", "data_sample", "data_description", "analysis", "num_recommendations"],
            template=recommendation_prompt
        )

        rec_chain = LLMChain(llm=self.llm, prompt=rec_template)

        rec_response = rec_chain.run(
            data_info=data_info,
            data_sample=data_sample,
            data_description=data_description,
            analysis=analysis,
            num_recommendations=num_recommendations
        )

        # Ensure response is a string
        rec_response_str = ensure_string(rec_response)

        formatted_rec_prompt = recommendation_prompt.format(
            data_info=data_info,
            data_sample=data_sample,
            data_description=data_description,
            analysis=analysis,
            num_recommendations=num_recommendations
        )
        self.memory.append(HumanMessage(content=formatted_rec_prompt))
        self.memory.append(AIMessage(content=rec_response_str))
        self.db.saveMemory(
            reportID=self.report_id,
            llm=self.db.llm_id_by_name(self.llm.model),
            prompet=formatted_rec_prompt,
            response=rec_response_str,
            chat=False
        )

        return rec_response_str 