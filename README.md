<p align="center">
  <b>日本語</b> | <a href="README.en.md">English</a>
</p>

# Sarashina Cookbook

Sarashina Cookbook は、Sarashina API を使ってアプリケーションを構築するためのコードとガイドを集めたリポジトリです。
Sarashina API に興味がある方が、どのような使い方があるかを調べ、自分のプロジェクトに取り入れやすい形のサンプルコードを見つけられる場所を目指しています。

## Sarashina API

この Cookbook のレシピを動かすには、Sarashina API の API キーが必要です。[sarashina.ai](https://sarashina.ai/#japanese) から無料で取得できます。

## セットアップ

```bash
git clone https://github.com/sbintuitions/sarashina-cookbook.git
cd sarashina-cookbook
uv sync --locked
```

`.env.sample` をコピーして `.env` を作り、API キーを設定してください。

```
SARASHINA_API_KEY=xxx
```

Sarashina の API を初めて使う方は、まず[公式の API ドキュメント](https://docs.sarashina.ai)のクイックスタートで基本的な呼び出し方を確認することをおすすめします。

## レシピ一覧

### RAG(検索拡張生成)

- [Sarashina を利用した RAG システム実現例]()
- [Sarashina を利用した RAG 検索精度の改善 (1/2)](https://www.sbintuitions.co.jp/blog/entry/2026/11/12/170000)

### コーディングエージェント

- [Sarashina をコーディングエージェントで使う: OpenCode・Hermes Agent・Crush での利用と、サブエージェントとしての活用](https://www.sbintuitions.co.jp/blog/entry/2026/11/06/100000)

## 関連リンク

- [Sarashina API ドキュメント](https://docs.sarashina.ai)
- [Sarashina 公式サイト](https://sarashina.ai)
- [SB Intuitions 公式サイト](https://www.sbintuitions.co.jp)

## ライセンス

このリポジトリは MIT ライセンスで公開しています。詳細は [LICENSE](LICENSE) を参照してください。
