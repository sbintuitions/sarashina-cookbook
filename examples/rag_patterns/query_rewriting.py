from common import chat, generate_answer, search_by_embedding

DOCUMENTS = [
    "タケシバホームアプリは、タケシバ製作所の家電をスマートフォンから操作できる無料のアプリである。",
    "タケシバホームアプリは、iOS 16以上と、Android 12以上に対応している。",
    "タケシバホームアプリは、アプリストアで「タケシバホーム」と検索するとインストールできる。",
    "タケシバホームアプリに登録できる機器は、1つのアカウントにつき最大5台である。",
    "タケシバホームアプリで「認証エラー」が表示された場合は、ログイン画面の「パスワードを忘れた方」からパスワードを再設定する。",
    "パスワードの再設定用のメールは、登録したメールアドレスに送られる。",
    "タケシバホームアプリの画面表示は、設定から文字サイズを変更できる。",
    "タケシバホームアプリは、機器の運転状況を通知で知らせる。",
    "アカウントを削除すると、登録していた機器の設定も消える。",
    "タケシバホームアプリの利用には、インターネット接続が必要である。",
]
QUESTION = "タケシバのアプリ、開こうとすると弾かれるんだけど、どうしたらいい?"

REWRITE_PROMPT_TEMPLATE = """
以下のユーザーの質問を、文書を検索するためのクエリに書き換えてください。

- 話し言葉を、書き言葉に直す
- 省略されている語や前提を補う
- 疑問文ではなく、探している情報を説明する文にする
- 書き換えたクエリだけを、1行で出力する

質問：{question}
"""


def rewrite_query(question: str) -> str:
    return chat(REWRITE_PROMPT_TEMPLATE.format(question=question)).strip()


rewritten = rewrite_query(QUESTION)
print("書き換え後のクエリ:", rewritten)

baseline_doc = DOCUMENTS[search_by_embedding(QUESTION, DOCUMENTS, top_n=1)[0]]
rewritten_doc = DOCUMENTS[search_by_embedding(rewritten, DOCUMENTS, top_n=1)[0]]

print("ベースライン:", baseline_doc)
print("書き換え:", rewritten_doc)
print(generate_answer(QUESTION, baseline_doc))
print("---")
print(generate_answer(QUESTION, rewritten_doc))
