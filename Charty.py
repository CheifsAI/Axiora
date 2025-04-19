from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import OllamaLLM
from typing import Dict, List, Tuple
import re

class Charty:
    def __init__(self, model_name="llama3.2:3b"):
        self.llm = OllamaLLM(model=model_name, temperature=0.4)
            
    def select_chart_type(self, data_info: Dict, question: str) -> str:
        self.chart_type_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at selecting chart types for data visualization. Strictly follow these rules:
            
            1. CHART SELECTION GUIDE:
            - For comparing categories: Bar or HorizontalBar
            - For trends over time: Line
            - For parts of a whole: Pie (few categories)
            - For relationships: Scatter
            - For precise values across many categories: Dot
            
            3. OUTPUT FORMAT (EXACTLY):
            chart_type: [Bar|HorizontalBar|Line|Pie|Scatter|StackedBar|Dot]
            
            Data Description: {data_description}
            Available Columns: {columns}
            Sample Data: {sample_data}
            Question: {question}
            
            Respond ONLY with:
            chart_type: [chart_type]""")
        ])

        """Select only the chart type based on the question and data."""
        chain = self.chart_type_prompt | self.llm
        response = chain.invoke({
            "data_description": data_info.get("description", ""),
            "columns": ", ".join(data_info.get("data_cols", [])),
            "sample_data": str(data_info.get("head", "")),
            "question": question
        })
        
        # Parse response
        chart_match = re.search(r'chart_type:\s*([a-zA-Z]+)', response, re.IGNORECASE)
        chart_type = chart_match.group(1) if chart_match else None
        
        # Validate
        allowed_charts = {'Bar', 'HorizontalBar', 'Line', 'Pie', 'Scatter', 
                        'StackedBar', 'Dot'}
        return chart_type if chart_type in allowed_charts else 'Bar'
    
    def select_columns(self, data_info: Dict, question: str) -> List[str]:
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

        """Select only the relevant columns based on the question and data."""
        chain = self.columns_prompt | self.llm
        response = chain.invoke({
            "data_description": data_info.get("description", ""),
            "columns": ", ".join(data_info.get("data_cols", [])),
            "sample_data": str(data_info.get("head", "")),
            "question": question
        })
        
        # Parse response
        cols_match = re.search(r'columns:\s*\[([^\]]+)\]', response)
        if cols_match:
            columns = [col.strip() for col in cols_match.group(1).split(',')]
        else:
            # Fallback parsing
            cols_line = next((line for line in response.split('\n') if line.startswith('columns:')), '')
            columns = [col.strip() for col in cols_line.replace('columns:', '').split(',') if col.strip()]
        
        # Validate columns exist in data
        available_cols = data_info.get("data_cols", [])
        return [col for col in columns if col in available_cols]
    
    def get_chart_recommendation(self, data_info: Dict, question: str) -> Tuple[str, List[str]]:
        """Combined recommendation (maintaining original interface)"""
        chart_type = self.select_chart_type(data_info, question)
        columns = self.select_columns(data_info, question)
        return chart_type, columns
"""
from langchain_ollama import OllamaLLM

llm = OllamaLLM(
    model="llama3",
    temperature=0.3,  # Less randomness
    top_p=0.9,        # Exclude unlikely tokens
    repeat_penalty=1.2  # Avoid repetition
)


"""