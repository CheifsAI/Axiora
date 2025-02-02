from langchain_ollama import OllamaLLM
llama3b = OllamaLLM(model="llama3.2:3b")
granite_code3b = OllamaLLM(model="granite-code:3b")
starcoder2 = OllamaLLM(model="starcoder2:3b")
class LLModels():
    def __init__(self, model_name, model):
        self.model_name = model_name
        self.model = model