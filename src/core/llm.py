class LLMClient:
    def __init__(self,model_name:str):
        self.model_name=model_name
    
    def generate(self, prompt:str)->str:
        
        return f"[{self.model_name}] Echo: {prompt}"
        