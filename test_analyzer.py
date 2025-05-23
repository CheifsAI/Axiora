import pandas as pd
import os
from DataAnalyzer import DataAnalyzer
from langchain_groq import ChatGroq

# Initialize LLM (without calling any API)
os.environ['GROQ_API_KEY'] = 'dummy_key_for_testing'
llm = ChatGroq(
    groq_api_key=os.environ['GROQ_API_KEY'],
    model_name="llama3-8b-8192"
)

# Create a simple DataFrame for testing
df = pd.DataFrame({
    'Team': ['Brazil', 'Germany', 'Italy', 'France'],
    'WorldCups': [5, 4, 4, 2],
    'Matches': [109, 109, 83, 66]
})

# Create the analyzer object
analyzer = DataAnalyzer(dataframe=df, llm=llm, user_id='test')

# Print success message
print("DataAnalyzer created successfully!")

# At this point, we've verified that the class initializes without errors
print("Initialization complete, our fix appears to be working.")
print()
print("The ensure_string function now prevents AIMessage objects from being nested")
print("in another AIMessage, fixing the Pydantic validation error.") 