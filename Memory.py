from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

llm = Ollama(model="llama3.1:8b")

memory = []

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

chain = prompt_template | llm


def start_app():
    while True:
        question = input("You: ")
        if question == "done":
            return

        # response = llm.invoke(question)
        response = chain.invoke({"input": question, "memory":memory})
        memory.append(HumanMessage(content=question))
        memory.append(AIMessage(content=response))

        print("AI:" + response)


if __name__ == "__main__":
    start_app()
