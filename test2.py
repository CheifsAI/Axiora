import pandas as pd
from DataAnalyzer import DataAnalyzer
from Models import llama3b
from collections import deque

df = pd.read_csv("Test_Datasets/WorldCupMatches.csv")
questions = ["Who is the most teams played as home team?", "Who is the most teams played as away team?"]
analyzer = DataAnalyzer(llm=llama3b, dataframe=df)
max_retries = 3  # Maximum retry attempts per question

# Create a queue with (question, attempt_count)
process_queue = deque([(q, 0) for q in questions])
execution_context = {'df': df}  # Maintain execution context

while process_queue:
    question, attempts = process_queue.popleft()
    
    try:
        # Generate code for the current question
        generated_codes = analyzer.visual(questions_list=[question])
        
        if not generated_codes:
            print(f"No code generated for: {question}")
            continue
            
        code = generated_codes[0]
        
        # Execute with current context
        exec(code, execution_context)
        print(f"Successfully executed: {question}")
        print(f"Code:\n{code}\n{'='*50}\n")
        
    except Exception as e:
        print(f"Error in '{question}': {str(e)}")
        if attempts < max_retries:
            print(f"Re-queueing for retry ({attempts+1}/{max_retries})")
            process_queue.append((question, attempts + 1))
        else:
            print(f"Max retries exceeded for: {question}")

print("Processing complete")