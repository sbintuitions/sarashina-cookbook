import os
from functools import cache

import numpy as np
import requests
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = "https://api.sarashina.ai/v1"
HEADERS = {
    "Authorization": f"Bearer {os.environ['SARASHINA_API_KEY']}",
    "Content-Type": "application/json",
}
EMBEDDING_MODEL = "sarashina3-embedding"
CHAT_MODEL = "sarashina3-mini"


def chat(prompt: str) -> str:
    response = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers=HEADERS,
        json={"model": CHAT_MODEL, "messages": [{"role": "user", "content": prompt}]},
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


@cache
def embed_text(text: str, task_type: str) -> list[float]:
    response = requests.post(
        f"{API_BASE_URL}/embeddings",
        headers=HEADERS,
        json={"model": EMBEDDING_MODEL, "input": text, "task_type": task_type},
    )
    response.raise_for_status()
    return response.json()["data"][0]["embedding"]


def search_by_embedding(query: str, documents: list[str], top_n: int) -> list[int]:
    query_emb = np.asarray(embed_text(query, "RETRIEVAL_QUERY"))
    docs_emb = np.asarray([embed_text(doc, "RETRIEVAL_DOCUMENT") for doc in documents])

    similarities = (docs_emb @ query_emb) / (
        np.linalg.norm(docs_emb, axis=1) * np.linalg.norm(query_emb)
    )
    return np.argsort(similarities)[::-1][:top_n].tolist()


PROMPT_TEMPLATE = """
以下のユーザーからの質問に対して、参考文書に記載されている情報を用いて回答してください。

質問：{question}
参考文書：{rel}
"""


def generate_answer(question: str, document: str) -> str:
    return chat(PROMPT_TEMPLATE.format(question=question, rel=document))
