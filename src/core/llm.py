
"""
class LLMClient:
    def __init__(self, model_name: str):
        self.model_name = model_name

    def generate(self, prompt: str) -> str:
        return f"[{self.model_name}] Echo: {prompt}"


"""

from transformers import pipeline
import torch
from src.core.config import get_logger 
logger = get_logger()   


class LLMClient:
    def __init__(self, model_name: str, max_new_tokens: int, temperature: float = 0.0):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        try:
            self.generator = pipeline(
                "text-generation",
                model=model_name,
                device_map='auto',
                trust_remote_code=False,
            )
        except Exception as e:
            # If model loading fails, fall back to a simple echo behavior
            logger.error(f"Failed to load model {model_name}: {e}")
            print(f"Failed to load model {model_name}: {e}", flush=True)
            self.generator = None

    def generate(self, prompt: str) -> str:
        # If the generator wasn't initialised, return a deterministic echo
        if self.generator is None:
            return f"[{self.model_name}] Echo: {prompt}"

        # Call the text-generation pipeline with a plain prompt
        do_sample = self.temperature > 0.0
        output = self.generator(
            prompt, 
            max_new_tokens=self.max_new_tokens, 
            do_sample=do_sample,
            temperature=self.temperature if do_sample else None
        )

        # Typical pipeline output: a list with one dict containing 'generated_text'
        if isinstance(output, list) and len(output) > 0:
            first = output[0]
            if isinstance(first, dict) and "generated_text" in first:
                gen = first["generated_text"]
                if isinstance(gen, str):
                    return gen
                # Handle case where generated content is a list of dicts
                if isinstance(gen, list):
                    parts = []
                    for item in gen:
                        if isinstance(item, dict):
                            if "content" in item:
                                parts.append(item["content"])
                            elif "text" in item:
                                parts.append(item["text"])
                        elif isinstance(item, str):
                            parts.append(item)
                    return "".join(parts)

            # Fallback: try make it string the first element
            try:
                return str(first)
            except Exception:
                return ""

        # Final fallback: make it string the whole output
        return str(output)
