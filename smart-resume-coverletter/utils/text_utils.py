import re
from collections import Counter
from typing import List


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\t", " ", text)
    text = re.sub(r"\u00A0", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def top_keywords(text: str, k: int = 25) -> List[str]:
    words = re.findall(r"[A-Za-z][A-Za-z\-\+0-9]{2,}", text.lower())
    stop = {
        "the","and","for","with","from","that","this","have","has","are","was","were","your","our","their","you","they","them","she","him","her","his","its","but","not","all","any","can","will","may","might","able","over","under","into","onto","out","off","per","via","of","in","on","to","as","by","at","be","is","am","or","a","an"
    }
    filtered = [w for w in words if w not in stop]
    freq = Counter(filtered)
    return [w for w, _ in freq.most_common(k)]