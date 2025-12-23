
class LLMClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        return f"[{self.model_name}] Echo: {prompt}"

# transformers
# torch
# accelerate
# from transformers import pipeline
# # import torch

# class LLMClient:  
#     # This loads the Phi-3 model computer's memory
#     def __init__(self,model_name: str):
#         self.generator = pipeline("text-generation",
#                                   model=model_name,
#                                   device_map="auto",
#                                   trust_remote_code=False)

#     def generate(self, prompt: str):
#         messages = [{"role": "user", 
#                      "content": prompt}]
#         output = self.generator(messages, 
#                                 max_new_tokens=100, 
#                                 do_sample=False)
#         return output[0]['generated_text'][-1]['content']
