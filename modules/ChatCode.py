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
###########################################
## Agent ##
###########################################
    def chat(self, question):
        try:
            agent = create_pandas_dataframe_agent(
                self.llm,
                self.dataframe,
                verbose=True,
                agent_type="zero-shot-react-description",
                allow_dangerous_code=True,
                handle_parsing_errors=True  
            )
            response = agent.invoke(question)
            
            if not response:
                response = "Try again"
            else:
                self.db.saveMemory(
                    reportID=self.report_id,
                    llm=self.db.llm_id_by_name(self.llm.model),
                    prompet=question,  
                    response=response,
                    chat=True
                )
            if response:
                self.memory.append(HumanMessage(content=question))
                self.memory.append(AIMessage(content=response))
                
        except ValueError as ve:
            print(f"Value error: {ve}")
            response = "I couldn't process that data request properly."

        except Exception as e:
            print(f"An error occurred: {e}")
            response = "Try again"  

        return response      
