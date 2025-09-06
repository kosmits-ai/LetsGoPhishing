import json
from jsonschema import validate, ValidationError
from .prompts import SYSTEM_PROMPT, SCHEMA, build_user_message
from .llm import call_llm
from .llm import call_ollama
import logging


logger = logging.getLogger(__name__)

def validate_response(payload: dict):
    try:
        validate(instance=payload, schema=SCHEMA)
    except ValidationError as e:
        raise ValueError(f"Response validation error: {e.message}")
    return True

def get_verdict(provider, model, parsed_email: dict, temperature=0.0, max_tokens=400) -> dict:
    input_json = build_user_message(parsed_email)
    base_messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": input_json}
    ]
    provider = provider.lower()
    if provider == "openai" and  model:
        raw = call_llm(model=model, messages=base_messages, temperature=temperature, max_tokens=max_tokens)
    elif provider == "ollama" and  model:
        raw = call_ollama(model=model, messages=base_messages, temperature=temperature, max_tokens=max_tokens)
    else:
        raise ValueError(f"Unknown provider: {provider}")
    try:
        response = json.loads(raw)
        #validate_response(response)
        return response
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {e}. Raw response: {raw}")
        raise ValueError(f"Failed to parse LLM response as JSON: {e}")
    except Exception as e:
        retry_messages = base_messages + [{
            "role": "system",
            "content": f"Your previous output failed schema validation. Error: {e}. "
                       "Return ONLY valid JSON per the schema, nothing else."
        }]
        if provider == "openai":
            raw_second = call_llm(model=model, messages=retry_messages, temperature=temperature, max_tokens=max_tokens)
        elif provider == "ollama":
            raw_second = call_ollama(model=model, messages=retry_messages, temperature=temperature, max_tokens=max_tokens)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        data_second = json.loads(raw_second)
        validate_response(data_second)
        return data_second