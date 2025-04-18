from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from typing import Dict, List, Tuple
import pandas as pd
import re

class ChartSelector:
    def __init__(self, model_name="llama3.2:3b"):
        self.llm = Ollama(model=model_name)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system",  """You are an expert data visualization assistant that recommends optimal chart types and precise columns for data analysis. Follow these rules strictly:

            1. CHART SELECTION GUIDE:
            - Bar: Comparing categories or groups (vertical bars)
            - HorizontalBar: Comparing many categories (horizontal bars)
            - Line: Showing trends over time (must have time dimension)
            - Pie: Displaying parts of a whole (use only for 2-5 categories)
            - Scatter: Revealing relationships between two numerical variables
            - StackedBar: Showing composition of categories
            - Histogram: Displaying distribution of a single numerical variable
            - Dot: Comparing many categories with precise values

            2. COLUMN SELECTION RULES:
            - Foucs on the columns that its name appered on the question
            - For "by [category]" questions: Use categorical columns
            - For metrics: Use numerical columns
            - For time trends: Use date columns
            - Never recommend columns not in Available Columns list

            3. OUTPUT FORMAT (MUST FOLLOW EXACTLY):
            chart_type: [Bar|HorizontalBar|Line|Pie|Scatter|StackedBar|Histogram|Dot]
            columns: [exact_column_name1, exact_column_name2]

            4. SPECIAL CASES:
            - "trend" or "over time": Line chart with date column
            - "distribution": Histogram
            - "compare": Bar/HorizontalBar
            - "composition": StackedBar or Pie (only if few categories)
            - "relationship": Scatter

            Data Description: {data_description}
            Available Columns: {columns}
            Sample Data: {sample_data}

            Question: {question}

            Respond ONLY in this exact format with NO additional text:
            chart_type: [chart_type]
            columns: [column1, column2]""")
        ])
    
    def get_chart_recommendation(self, data_info: Dict, question: str) -> Tuple[str, List[str]]:
        """Get chart type and columns recommendation based on data and question."""
        chain = self.prompt_template | self.llm
        response = chain.invoke({
            "data_description": data_info.get("description", ""),
            "columns": ", ".join(data_info.get("data_cols", [])),
            "sample_data": str(data_info.get("head", "")),
            "question": question
        })
        
        # Improved parsing with regex to handle different response formats
        chart_type = None
        columns = []
        
        # Try to extract chart type
        chart_match = re.search(r'chart_type:\s*([a-zA-Z]+)', response, re.IGNORECASE)
        if chart_match:
            chart_type = chart_match.group(1)
        
        # Try to extract columns
        cols_match = re.search(r'columns:\s*([^\n]+)', response)
        if cols_match:
            columns = [col.strip() for col in cols_match.group(1).split(',')]
        
        # Fallback to simple parsing if regex fails
        if not chart_type or not columns:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            if len(lines) >= 2:
                chart_type = lines[0].replace("chart_type:", "").strip()
                columns = [col.strip() for col in lines[1].replace("columns:", "").split(',')]
        
        # Validate chart type against allowed values
        allowed_charts = {'Bar', 'HorizontalBar', 'Line', 'Histogram', 'Pie', 'Scatter', 'StackedBar', 'Dot'}
        if chart_type not in allowed_charts:
            chart_type = 'Bar'  # default fallback
        
        # Validate columns exist in data
        available_cols = data_info.get("data_cols", [])
        columns = [col for col in columns if col in available_cols]
        
        return chart_type, columns