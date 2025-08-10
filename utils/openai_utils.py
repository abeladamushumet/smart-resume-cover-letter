import os
from typing import Dict, Any
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()

try:
    from openai import OpenAI
except Exception:  # Fallback if library missing at import time
    OpenAI = None  # type: ignore


class ModelConfig(BaseModel):
    model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    temperature: float = 0.7
    max_tokens: int | None = None


def get_client() -> Any:
    """Return an OpenAI client instance. Assumes OPENAI_API_KEY is set."""
    if OpenAI is None:
        raise RuntimeError("openai package not installed. Please install dependencies.")
    return OpenAI()


def generate_text(prompt: str, variables: Dict[str, str] | None = None, config: ModelConfig | None = None) -> str:
    """
    Basic LLM call that performs simple string substitution on the prompt using variables
    and returns the model's text output.
    """
    if variables:
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            prompt = prompt.replace(placeholder, value)

    if config is None:
        config = ModelConfig()

    client = get_client()

    # New OpenAI SDK responses API
    response = client.responses.create(
        model=config.model,
        temperature=config.temperature,
        max_output_tokens=config.max_tokens,
        input=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )

    # Extract the first text output
    try:
        output_text = response.output_text  # SDK helper
    except Exception:
        # Fallback extraction
        output_text = ""
        if hasattr(response, "output") and response.output:
            for item in response.output:
                if item.get("type") == "message":
                    for content in item.get("content", []):
                        if content.get("type") == "output_text":
                            output_text += content.get("text", "")
    return output_text.strip()