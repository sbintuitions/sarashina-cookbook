import requests
from common import API_BASE_URL, HEADERS, generate_answer, search_by_embedding

RERANK_MODEL = "sarashina3-rerank"

DOCUMENTS = [
    "電気ケトル「わかしたて」は、容量1.0Lで、沸騰すると自動で電源が切れる。",
    "電気ケトル「わかしたて」の無償修理は、購入日から2年間受けられる。対象は本体のみで、パッキンなどの消耗品や、落下による破損は含まれない。",
    "炊飯器「ふっくら」の保証期間は、購入日から3年間である。",
    "「わかしたて」の保証期間中に故障した場合は、サポート窓口に連絡する。",
    "「わかしたて」の保証期間を過ぎた後の修理は、有償となる。",
    "「わかしたて」の保証期間について不明な点は、サポート窓口で案内している。",
    "「わかしたて」の保証書は、購入日の記載がないと無効になる場合がある。",
    "「わかしたて」の取扱説明書は、公式サイトからダウンロードできる。",
    "炊飯器「ふっくら」は、5.5合炊きである。",
    "「わかしたて」は、白と黒の2色で展開されている。",
]
QUESTION = "「わかしたて」の保証期間は何年ですか?"


def rerank(query: str, documents: list[str]) -> list[int]:
    response = requests.post(
        f"{API_BASE_URL}/rerank",
        headers=HEADERS,
        json={
            "model": RERANK_MODEL,
            "query": query,
            "documents": documents,
            "task_type": "GENERAL_QA",
        },
    )
    response.raise_for_status()
    result = response.json()["data"][0]["result"]
    return [item["document_id"] for item in result]


candidate_ids = search_by_embedding(QUESTION, DOCUMENTS, top_n=5)
candidates = [DOCUMENTS[i] for i in candidate_ids]

# ベースライン: Embedding の1位
baseline_doc = candidates[0]

# リランカー: 5件を並べ替えた1位
reranked_ids = rerank(QUESTION, candidates)
reranked_doc = candidates[reranked_ids[0]]

print("ベースライン:", baseline_doc)
print("リランカー:", reranked_doc)
print(generate_answer(QUESTION, baseline_doc))
print("---")
print(generate_answer(QUESTION, reranked_doc))
