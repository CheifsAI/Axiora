from langchain_core.prompts import ChatPromptTemplate
from langchain_community.llms import Ollama
from typing import Dict, List, Tuple
import pandas as pd
import re

class ChartSelector:
    def __init__(self, model_name="llama3.2:3b"):
        self.llm = Ollama(model=model_name)
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """You are an expert data visualization assistant. Analyze the following data and question to recommend:
1. The best chart type (choose from: Bar, HorizontalBar, Line, Histogram, Pie, Scatter, StackedBar, Dot)
2. The exact column names to use from the provided dataframe

Data Description: {data_description}
Available Columns: {columns}
Sample Data: {sample_data}

Question: {question}

Respond ONLY in this exact format:
chart_type: [one of the allowed chart types]
columns: [comma-separated exact column names]

DO NOT include any other text, explanations, or examples in your response."""),
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
            chart_type = chart_match.group(1).lower()
        
        # Try to extract columns
        cols_match = re.search(r'columns:\s*([^\n]+)', response)
        if cols_match:
            columns = [col.strip() for col in cols_match.group(1).split(',')]
        
        # Fallback to simple parsing if regex fails
        if not chart_type or not columns:
            lines = [line.strip() for line in response.strip().split('\n') if line.strip()]
            if len(lines) >= 2:
                chart_type = lines[0].replace("chart_type:", "").strip().lower()
                columns = [col.strip() for col in lines[1].replace("columns:", "").split(',')]
        
        # Validate chart type against allowed values
        allowed_charts = {'bar', 'horizontalbar', 'line', 'histogram', 'pie', 'scatter', 'stackedbar', 'dot'}
        if chart_type not in allowed_charts:
            chart_type = 'bar'  # default fallback
        
        # Validate columns exist in data
        available_cols = data_info.get("data_cols", [])
        columns = [col for col in columns if col in available_cols]
        
        return chart_type, columns