"""
Improved chat function for DataAnalyzer class
"""

def chat(self, question: str) -> str:
    """
    Interact with the data analysis system to answer questions about the dataset.
    
    Args:
        question: User's question about the data
        
    Returns:
        The model's response with data-informed insights
    """
    # Create a more informative system prompt with dataset context
    system_prompt = f"""
    You are a data analyst with expertise in analyzing {self.dataframe.shape[1]} variables across {self.dataframe.shape[0]} records.

    Dataset context:
    - Type of data: {self.data_info.splitlines()[0] if self.data_info else 'Unknown dataset'}
    - Key columns: {', '.join(self.dataframe.columns[:5]) if len(self.dataframe.columns) > 5 else self.data_cols}
    - Total rows: {self.dataframe.shape[0]}
    - Data summary: {self.data_description[:200]}...

    Instructions:
    - Answer using ONLY the data available
    - Support answers with specific metrics when possible
    - If asked about unknown variables, respond transparently
    - Prioritize clarity, relevance, and actionable insights
    - Use visualizations when appropriate (suggest chart types)
    """

    # Create the chat prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}")
    ])

    # Create and invoke the chain
    chain = prompt | self.llm
    
    try:
        response = chain.invoke({
            "chat_history": self.memory,
            "question": question
        })
        
        # Save to memory and database
        self.memory.append(HumanMessage(content=question))
        self.memory.append(AIMessage(content=response))
        
        self.db.saveMemory(
            reportID=self.report_id,
            llm=self.db.llm_id_by_name(self.llm.model),
            prompet=question,
            response=response,
            chat=True
        )
        
        return response
        
    except Exception as e:
        error_msg = f"Error processing chat request: {str(e)}"
        print(error_msg)
        return f"I encountered an issue analyzing your question. Please try rephrasing or providing more context. Technical details: {str(e)}"