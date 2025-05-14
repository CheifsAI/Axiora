# DataAnalyzer Documentation

## Overview

The `DataAnalyzer` class provides a comprehensive solution for data analysis and cleaning using Large Language Models (LLMs). This class simplifies the process of preparing, cleaning, analyzing, and visualizing data by leveraging the power of LLMs to generate insights and recommendations.

## Table of Contents

1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Data Cleaning](#data-cleaning)
   - [Recommending Cleaning Strategies](#recommending-cleaning-strategies)
   - [Applying Cleaning Operations](#applying-cleaning-operations)
   - [Restoring Original Data](#restoring-original-data)
4. [Data Analysis](#data-analysis)
   - [Generating Analysis Reports](#generating-analysis-reports)
   - [Generating Analytical Questions](#generating-analytical-questions) 
   - [Creating Recommendations](#creating-recommendations)
5. [Interactive Features](#interactive-features)
   - [Chat Interface](#chat-interface)
   - [Visualization Recommendations](#visualization-recommendations)
6. [Advanced Usage](#advanced-usage)
7. [API Reference](#api-reference)

## Installation

Ensure you have the required dependencies installed:

```bash
pip install pandas numpy langchain langchain_openai
```

## Basic Usage

Here's a simple example of how to use the `DataAnalyzer` class:

```python
from DataAnalyzer import DataAnalyzer
import pandas as pd
from langchain_openai import ChatOpenAI

# Load your data
df = pd.read_csv("your_data.csv")

# Initialize an OpenAI LLM (or any other supported LLM)
llm = ChatOpenAI(api_key="your_api_key")

# Create a DataAnalyzer instance
analyzer = DataAnalyzer(df, llm)

# Generate an analysis report
analysis = analyzer.analysis_data()
print(analysis)
```

## Data Cleaning

The `DataAnalyzer` class provides powerful data cleaning capabilities with intelligent recommendations.

### Recommending Cleaning Strategies

Before cleaning the data, you can get recommendations on which cleaning strategies are appropriate for your dataset:

```python
# Get recommendations for cleaning strategies
cleaning_strategies = analyzer.recommend_cleaning_strategy()
print(cleaning_strategies)
```

This will return a dictionary with recommended strategies for handling:
- Missing values
- Duplicates
- Outliers
- Special characters
- Data type conversions

### Applying Cleaning Operations

You can apply the recommended strategies or specify your own:

```python
# Use recommended strategies
cleaned_df = analyzer.clean_data(cleaning_strategies)

# Or specify custom strategies
custom_strategies = {
    'missing_values': 'mean',
    'duplicates': 'drop_first',
    'outliers': 'iqr',
    'special_chars': 'remove'
}
cleaned_df = analyzer.clean_data(custom_strategies)
```

For column-specific strategies:

```python
column_specific = {
    'missing_values': {
        'age': 0,  # Replace missing values in 'age' with 0
        'income': 'median',  # Replace missing values in 'income' with median
        'city': 'mode'  # Replace missing values in 'city' with mode
    },
    'outliers': 'iqr'  # Use IQR method for all numerical columns
}
cleaned_df = analyzer.clean_data(column_specific)
```

### Restoring Original Data

If you need to revert to the original data:

```python
original_df = analyzer.restore_original_data()
```

## Data Analysis

### Generating Analysis Reports

Generate a comprehensive analysis report:

```python
analysis_report = analyzer.analysis_data()
```

The report includes:
- Executive summary
- Key patterns and strategic insights
- Statistical validation and modeling
- Risks, anomalies, and data limitations
- Opportunities for growth and optimization
- Hidden or surprising insights
- Strategic recommendations

### Generating Analytical Questions

Generate insightful questions that can be answered with the data:

```python
# Generate 5 analytical questions
questions = analyzer.questions_gen(5)
for i, question in enumerate(questions, 1):
    print(f"{i}. {question}")
```

### Creating Recommendations

Generate strategic business recommendations based on the analysis:

```python
# Generate 3 recommendations
recommendations = analyzer.generate_recommendations(3)
print(recommendations)
```

## Interactive Features

### Chat Interface

Interact with the data through a natural language interface:

```python
response = analyzer.chat("What are the key factors affecting customer satisfaction?")
print(response)

# Follow-up questions maintain context
response = analyzer.chat("How do these factors vary by customer segment?")
print(response)
```

### Visualization Recommendations

Get recommendations for visualizing answers to analytical questions:

```python
question = "How have monthly sales evolved over the past year?"
chart_type, columns = analyzer.get_chart_recommendation(question)

print(f"Recommended chart type: {chart_type}")
print(f"Recommended columns: {columns}")
```

## Advanced Usage

### Custom Cleaning Pipelines

You can create custom cleaning pipelines by calling methods sequentially:

```python
# First get recommendations
strategies = analyzer.recommend_cleaning_strategy()

# Modify the recommendations as needed
strategies['missing_values'] = 'mean'  # Override with mean imputation
strategies['outliers'] = 'zscore'  # Use Z-score for outlier detection

# Apply the modified strategies
cleaned_df = analyzer.clean_data(strategies)

# Get recommendations on the cleaned data
new_recommendations = analyzer.generate_recommendations()
```

### Working with the Cleaning Log

Review the cleaning operations that were performed:

```python
# Clean the data
analyzer.clean_data(strategies)

# Check the cleaning log
for log_entry in analyzer.cleaning_log:
    print(log_entry)
```

## API Reference

### DataAnalyzer Class

```python
DataAnalyzer(dataframe, llm, user_id=None)
```

**Parameters:**
- `dataframe` (pd.DataFrame): The dataframe to analyze
- `llm`: The large language model to use for analysis
- `user_id` (str, optional): User ID for tracking analytics

**Main Methods:**

- `recommend_cleaning_strategy() -> Dict`: Analyze the dataframe and recommend cleaning strategies
- `clean_data(strategies: Dict = None) -> pd.DataFrame`: Clean the dataset using various strategies
- `restore_original_data() -> pd.DataFrame`: Restore the dataframe to its original state
- `analysis_data() -> str`: Generate a comprehensive analysis report
- `questions_gen(num: int) -> List[str]`: Generate analytical questions
- `chat(question: str) -> str`: Answer questions about the data
- `select_chart_type(question: str) -> str`: Recommend a chart type for a question
- `select_columns(question: str) -> List[str]`: Recommend columns for a question
- `get_chart_recommendation(question: str) -> Tuple[str, List[str]]`: Get chart and column recommendations
- `generate_recommendations(num_recommendations: int = 5) -> str`: Generate business recommendations

**Properties:**
- `dataframe`: The current dataframe (potentially cleaned)
- `original_dataframe`: The original dataframe before any cleaning
- `cleaning_log`: Log of cleaning operations performed 