from common import chat, generate_answer, search_by_embedding

DOCUMENTS = [
    "タケシバ製作所の愛知工場は、1965年に稼働を開始した。",
    "愛知工場の従業員数は、約800人である。",
    "愛知工場では、主に炊飯器と電気ケトルを生産している。",
    "タケシバ製作所の福岡工場は、2010年に稼働を開始した。",
    "福岡工場では、主に洗濯機を生産している。",
    "福岡工場は、九州地方の物流拠点にも近い。",
    "タケシバ製作所は、国内に愛知工場と福岡工場の2つの工場を持つ。",
    "愛知工場の敷地面積は、約12万平方メートルである。",
    "福岡工場の見学は、事前予約制である。",
    "タケシバ製作所の本社は、愛知県にある。",
]
QUESTION = "福岡工場の立地には、どのような利点がありますか?"

PLAN_PROMPT_TEMPLATE = """
以下の質問へのドラフトから、事実についての主張を抜き出し、それぞれの根拠を確認するための質問を作ってください。

- ドラフトの主張ごとに、1つの質問にする。質問は、最大3つまで
- 「はい」「いいえ」では答えられない、「何」「どのように」などで尋ねる質問にする
- ドラフトの言い回しは使わず、主張の中心になる事実だけを尋ねる
- 1行に1つ、質問だけを出力する

質問：{question}
ドラフト：{draft}
"""

VERIFY_PROMPT_TEMPLATE = """
以下の質問への答えが、参考文書に書かれているかを確認してください。

- 質問に直接答える文が参考文書にある場合は、その文をそのまま引用する
- そうでない場合は、「記載なし」とだけ答える
- 推測や解釈は書かない。引用か「記載なし」のどちらかだけを出力する

質問：{question}
参考文書：{rel}
"""

REVISE_PROMPT_TEMPLATE = """
以下の質問に対するドラフトを、確認結果をもとに修正してください。

- 確認結果に引用がある主張だけを、回答に残す
- 確認結果が「記載なし」の質問に対応する主張は、回答から取り除く
- 取り除いた主張について、「文書に記載がある」などと書き足さない
- 修正後の回答だけを出力する

質問：{question}
ドラフト：{draft}
確認結果：
{verification}
"""


def plan_verification_questions(question: str, draft: str) -> list[str]:
    output = chat(PLAN_PROMPT_TEMPLATE.format(question=question, draft=draft))
    return [line.strip() for line in output.splitlines() if line.strip()]


def verify(verification_question: str, documents: list[str]) -> str:
    doc_id = search_by_embedding(verification_question, documents, top_n=1)[0]
    return chat(
        VERIFY_PROMPT_TEMPLATE.format(
            question=verification_question, rel=documents[doc_id]
        )
    )


def revise(question: str, draft: str, verification: str) -> str:
    return chat(
        REVISE_PROMPT_TEMPLATE.format(
            question=question, draft=draft, verification=verification
        )
    )


doc_id = search_by_embedding(QUESTION, DOCUMENTS, top_n=1)[0]
print("検索された文書:", DOCUMENTS[doc_id])

draft = generate_answer(QUESTION, DOCUMENTS[doc_id])
print("ドラフト:", draft)

verification_questions = plan_verification_questions(QUESTION, draft)
print("検証用の質問:", verification_questions)

results = [
    f"質問：{vq}\n回答：{verify(vq, DOCUMENTS)}" for vq in verification_questions
]
verification = "\n\n".join(results)
print("検証結果:", verification)

print("修正後:", revise(QUESTION, draft, verification))
