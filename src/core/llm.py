# This file defines the LLMClient class, which is responsible for loading a language model
# and generating text based on prompts. 
# It uses the Hugging Face Transformers library to load the model and tokenizer, and includes 
# a simple caching mechanism to speed up repeated prompts.
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from src.core.config import get_logger 

logger = get_logger()   
class LLMClient:
    def __init__(self, model_name: str, max_new_tokens: int, temperature: float = 0.0):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self._generation_cache = {}  # Simple response cache
        
        try:
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map='auto',
                torch_dtype=torch.float16  
            )
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            # Set padding token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            print(f"Failed to load model {model_name}: {e}", flush=True)
            self.model = None
            self.tokenizer = None

    def generate(self, prompt: str) -> str:
        """Generate text with simple caching for duplicate prompts."""
        
        # If model wasn't initialized, return echo
        if self.model is None:
            return f"[{self.model_name}] Echo: {prompt}"
        
        # Check cache first
        cache_key = hash(prompt)
        if cache_key in self._generation_cache:
            logger.debug("Cache hit for prompt")
            return self._generation_cache[cache_key]
        
        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True).to(self.model.device)
        
        # Generate
        do_sample = self.temperature > 0.0
        gen_kwargs = {
            "max_new_tokens": self.max_new_tokens,
            "do_sample": do_sample,
            "pad_token_id": self.tokenizer.pad_token_id,
        }
        if do_sample:
            gen_kwargs["temperature"] = self.temperature
        
        with torch.no_grad():
            outputs = self.model.generate(**inputs, **gen_kwargs)
        
        # Decode only the new tokens (skip the input prompt)
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Cache and return
        self._generation_cache[cache_key] = generated_text
        return generated_text