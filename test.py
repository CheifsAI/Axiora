from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

# Initialize Ollama
llm = Ollama(model="llama3.2:3b")

# ====== Step 1: Chart Type Selection ======
chart_selection_template = """Analyze the following question and determine the most appropriate matplotlib chart type:
Question: {question}

Consider these guidelines:
- Time series data -> Line chart
- Comparisons between categories -> Bar chart
- Distributions -> Histogram
- Part-to-whole relationships -> Pie chart
- Correlations -> Scatter plot

Provide: 
1. Chart type (one word)
2. Brief reasoning (one sentence)"""

chart_selection_prompt = PromptTemplate(
    input_variables=["question"],
    template=chart_selection_template
)

chart_chain = LLMChain(
    llm=llm,
    prompt=chart_selection_prompt,
    output_key="chart_info"
)

# ====== Step 2: Code Generation ======
code_generation_template = """Generate matplotlib Python code for a {chart_type} that addresses:
Question: {question}

Include:
1. Sample data (or comments for data input)
2. Proper labels and titles
3. plt.show()
4. Brief comments explaining key elements

Format:
```python
[Your code here]
```"""

code_generation_prompt = PromptTemplate(
    input_variables=["question", "chart_type"],
    template=code_generation_template
)

code_chain = LLMChain(
    llm=llm,
    prompt=code_generation_prompt,
    output_key="code"
)

# ====== Full Pipeline ======
full_chain = SequentialChain(
    chains=[chart_chain, code_chain],
    input_variables=["question"],
    output_variables=["chart_info", "code"],
    verbose=True
)

# ====== Execution ======
question = "What's the sales over the years?"
result = full_chain.invoke({"question": question})

print(f"Chart Decision: {result['chart_info']}")
print(f"Generated Code:\n{result['code']}")