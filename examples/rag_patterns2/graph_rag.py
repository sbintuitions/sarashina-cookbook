from common import generate_answer, search_by_embedding

DOCUMENTS = [
    "「ひなた」は、タケシバ製作所が2024年に発売した家庭用のスマート給湯器である。スマートフォンから湯温や入浴時間を設定できる。開発責任者は浜松花子が務めた。",
    "浜松花子は、2018年から2021年まで「ぬくもりプロジェクト」のリーダーを務めた。2022年に給湯器事業部へ異動した。",
    "「ぬくもりプロジェクト」では、温度センサーで床暖房を自動制御するコントローラー「ほかほか」が開発された。",
    "「ほかほか」は、2020年の秋に発売された。",
    "「ひだまり」は、タケシバ製作所が2023年に発売した家庭用の電気ストーブである。開発責任者は大門太郎が務めた。",
    "大門太郎は、2015年から2019年まで「あおぞらプロジェクト」のリーダーを務めた。",
    "「あおぞらプロジェクト」では、衣類乾燥に使える除湿機「からっと」が開発された。「からっと」は2017年の春に発売された。",
    "タケシバ製作所は1962年に創業した家電メーカーで、本社は愛知県にある。",
    "タケシバ製作所の給湯器事業部は2022年に新設された。「ひなた」はこの事業部の最初の製品である。",
    "床暖房のコントローラーを選ぶときは、対応する熱源の種類や、設置する部屋の広さを確認するとよい。",
]
QUESTION = "「ひなた」の開発責任者が以前リーダーを務めたプロジェクトで開発された製品は、いつ発売されましたか?"

# エンティティから出る辺の一覧。辺は (関係, つながる先, 元の文書の番号)
GRAPH = {
    "ひなた": [("発売年", "2024年", 0), ("開発責任者", "浜松花子", 0)],
    "浜松花子": [
        ("リーダーを務めたプロジェクト", "ぬくもりプロジェクト", 1),
        ("異動先", "給湯器事業部", 1),
    ],
    "ぬくもりプロジェクト": [("開発した製品", "ほかほか", 2)],
    "ほかほか": [("発売時期", "2020年の秋", 3)],
    "ひだまり": [("発売年", "2023年", 4), ("開発責任者", "大門太郎", 4)],
    "大門太郎": [("リーダーを務めたプロジェクト", "あおぞらプロジェクト", 5)],
    "あおぞらプロジェクト": [("開発した製品", "からっと", 6)],
    "からっと": [("発売時期", "2017年の春", 6)],
    "タケシバ製作所": [("創業", "1962年", 7), ("本社の所在地", "愛知県", 7)],
    "給湯器事業部": [("新設", "2022年", 8), ("最初の製品", "ひなた", 8)],
}


def find_entities(question: str, graph: dict) -> list[str]:
    return [entity for entity in graph if entity in question]


def collect_doc_ids(graph: dict, start_entities: list[str], max_hops: int) -> list[int]:
    visited = set(start_entities)
    frontier = start_entities
    doc_ids: list[int] = []
    for _ in range(max_hops):
        next_frontier = []
        for entity in frontier:
            for _relation, target, doc_id in graph.get(entity, []):
                if doc_id not in doc_ids:
                    doc_ids.append(doc_id)
                if target not in visited:
                    visited.add(target)
                    next_frontier.append(target)
        frontier = next_frontier
    return doc_ids


start_entities = find_entities(QUESTION, GRAPH)
print("起点のエンティティ:", start_entities)

doc_ids = collect_doc_ids(GRAPH, start_entities, max_hops=4)
print("集めた文書の番号:", doc_ids)

graph_context = "\n".join(DOCUMENTS[i] for i in doc_ids)
baseline_doc = DOCUMENTS[search_by_embedding(QUESTION, DOCUMENTS, top_n=1)[0]]

print("ベースライン:", baseline_doc)
print(generate_answer(QUESTION, baseline_doc))
print("---")
print(generate_answer(QUESTION, graph_context))
