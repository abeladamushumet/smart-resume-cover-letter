import os
from typing import Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv

# OpenAI SDK (>=1.x)
try:
    from openai import OpenAI
except Exception as exc:  # pragma: no cover
    OpenAI = None  # type: ignore

load_dotenv()

_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

class OpenAIClientSingleton:
    _client: Optional["OpenAI"] = None

    @classmethod
    def get_client(cls) -> "OpenAI":
        if cls._client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("OPENAI_API_KEY is not set. Add it to your .env file.")
            if OpenAI is None:
                raise RuntimeError(
                    "openai package not available. Ensure it is installed from requirements.txt."
                )
            cls._client = OpenAI(api_key=api_key)
        return cls._client


@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
def generate_text(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: Optional[str] = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> str:
    """Generate text via OpenAI Chat Completions API.

    Raises on failure (tenacity will retry).
    """
    client = OpenAIClientSingleton.get_client()
    model_name = model or _DEFAULT_MODEL

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    content = response.choices[0].message.content or ""
    return content.strip()