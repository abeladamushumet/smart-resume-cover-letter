import re
from typing import List


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def truncate_words(text: str, max_words: int) -> str:
    words: List[str] = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."


def format_bullets(lines: List[str]) -> str:
    return "\n".join(f"- {line.strip()}" for line in lines if line.strip())