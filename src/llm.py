from openai import OpenAI
import os
from dotenv import load_dotenv
DEFAULT_TIMEOUT = 40
import time
import ollama

load_dotenv()

_client = None


def _client_llm():
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client


def call_llm(model, messages, temperature=0.0, max_tokens=400) -> str: #temperature 0 for low randomness
    client = _client_llm()
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                seed=30,
                response_format={"type": "json_object"},
                timeout=DEFAULT_TIMEOUT
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == 2: raise
            time.sleep(2 ** attempt)
    raise RuntimeError("Failed to get response from LLM after retries")


def call_ollama(model: str, messages, temperature=0.0, max_tokens=400) -> str: #temperature 0 for low randomness
        for attempt in range(3):
            try:
                result = ollama.chat(
                    model=model,
                    messages=messages,
                    options = {"temperature": temperature, "num_predict": max_tokens},
                    format="json"
                )
                return result['message']["content"]
            except Exception as e:
                if attempt == 2: raise
                time.sleep(2 ** attempt)
        raise RuntimeError(f"Failed to get response from LLM {model} after retries")