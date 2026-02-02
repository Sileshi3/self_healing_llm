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

    # # In generate()
    # def generate_with_cache(self, system_prompt: str, user_prompt: str):
    #     if self.system_prompt_cache is None:
    #         # First call: compute system prompt KV
    #         system_ids = self.tokenizer(system_prompt, return_tensors="pt").input_ids.to(self.model.device)
    #         with torch.no_grad():
    #             outputs = self.model(system_ids, use_cache=True)
    #             self.system_prompt_cache = outputs.past_key_values
        
    #     # Append user prompt to cached system prompt
    #     full_prompt = system_prompt + user_prompt
    #     # ... (complex, requires manual generation loop)
