# Sarashina をコーディングエージェントで使う: OpenCode・Hermes Agent・Crush での利用と、サブエージェントとしての活用

## はじめに

SB Intuitions 株式会社の林悠大です。

本稿では、コーディングエージェントに SarashinaサービスのAPI機能 を接続する方法を解説します。主な接続先は OpenCode で、メインモデルとして利用する方法と、**他のモデルのサブエージェントとして組み込む方法**を扱います。また、Hermes Agent や Crush での設定例、Claude Code から OpenCode へタスクを委譲して Sarashina を間接利用する構成も紹介します。なお、ここで紹介するコーディングエージェントで利用する使い方では**モデルが想定外の操作をすることもありますので、permissionを付けるなどして危険な操作をできないように設定しておくことを強く推奨します**。

## コーディングエージェントと SarashinaサービスのAPI機能 の接続方法

コーディングエージェントが LLM に求めるのは、Function Calling に対応した対話型 API です。エージェントは回答を一度生成して終了するだけでなく、ファイル読み取りやコマンド実行といったツール呼び出しの要求と結果の受け渡しを繰り返しながらタスクを遂行します。このように、LLM とツールの往復を担う仕組みは、一般に「ハーネス」と呼ばれます。

あるコーディングエージェントが SarashinaサービスのAPI機能 を利用できるかは、まずエージェントが要求する API 形式と、同機能が提供する形式が合致するかで決まります。対話エンドポイントは、OpenAI の Chat Completions と部分的に互換性のある形式のみを提供しています。主要エージェントとの相性は以下の通りです。

| コーディングエージェント | 要求する API の形式 | 直接接続可否 |
|------------------------|----------------------|--------------|
| OpenCode               | OpenAI 互換 (Chat Completions) | 可 |
| Claude Code            | Anthropic Messages API | 不可(形式の変換が必要) |
| Codex                  | OpenAI Responses API | 不可(形式の変換が必要) |

OpenCode は API の形式が一致するため、設定ファイルで接続先を指定するだけで直接利用できます。本稿ではこの経路を中心に紹介します。なお、同機能は以前、OpenCode が送信する一部の項目を受け付けず、直接接続には LiteLLM のようなプロキシでリクエストを補正する必要がありました。現在は API 側の更新でこれらの項目も受理されるようになったため、プロキシを介さず直接接続できます。

Claude Code と Codex は、Sarashina が提供していない形式で通信するため、直接はつながりません。これらから利用するにはプロキシで API 形式を変換する方法がありますが、本稿ではプロキシを立てずに済む構成として、後半で Claude Code から OpenCode へのタスク委譲を取り上げます。

このブログで紹介するモデルである Sarashina3.2 mini thinking は、一つ前の Sarashina3 mini からエージェント性能を大きく向上させたモデルであり、コーディングエージェントでの利用に適したモデルとなっています。このモデルの詳細については以下のブログで紹介されていますので、ぜひご覧ください。
https://www.sbintuitions.co.jp/blog/entry/2026/10/29/133000

## セットアップ

Sarashina の API キーは [sarashina.ai](https://sarashina.ai/#japanese) で取得し、環境変数 `SARASHINA_API_KEY` に設定してください。

```bash
export SARASHINA_API_KEY=<取得したAPIキー>
```

OpenCode から Sarashina へ直接接続するために、追加で用意するツールはありません。接続先の指定は、次のセクションで作成する OpenCode の設定ファイルに記述します。

## OpenCode で SarashinaサービスのAPI機能 のモデルを利用する

このセクションでは、Sarashina のモデルを OpenCode のメインのモデルとして利用する手順を紹介します。以降の説明は OpenCode v2.2.0 を利用したものになります。

### OpenCode のプロバイダ設定

OpenCode では、Sarashina を OpenAI 互換のカスタムプロバイダとして登録します。プロジェクトのルートに `opencode.json` を作成し、次の内容を記述します。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "providers": {
    "sarashina": {
      "name": "Sarashina",
      "env": ["SARASHINA_API_KEY"],
      "package": "@opencode/ai/providers/openai-compatible",
      "settings": {
        "baseURL": "https://api.sarashina.ai/v1"
      },
      "models": {
        "sarashina3.2-mini-thinking": {
          "name": "Sarashina3.2 mini thinking",
          "limit": { "context": 128000, "output": 32678 }
        }
      }
    }
  }
}
```

設定のポイントは次の通りです。

- `package`: `@opencode/ai/providers/openai-compatible` を指定すると、OpenAI 互換の API を提供する任意のエンドポイントをプロバイダとして登録できます
- `settings.baseURL`: SarashinaサービスのAPI機能 のエンドポイントを直接指定します
- `env`: ここに列挙した環境変数の値が、認証情報として送られます
- `models`: 利用したいモデルを列挙します。キーは Sarashina 側のモデル名と一致させます
- `limit.output: 32678`: OpenCode が要求する出力トークン数の既定値は、Sarashina の上限である 32678 と異なるため、API の上限に合わせてモデルごとに設定します

どのプロジェクトからも利用したい場合は、同じ内容を `~/.config/opencode/opencode.json` に記述します。

### 動作確認

`SARASHINA_API_KEY` を設定したターミナルで、プロジェクトのルートに移動して OpenCode を起動します。

```bash
opencode
```

TUI が起動したら、設定したプロバイダが認識されているかを確認します。`/models` コマンドを実行すると、モデルの選択肢に「Sarashina」の2つのモデルが表示されます。

接続確認として、次のような指示を投げてみます。

```text
hello.txt というファイルを作成して、「こんにちは」と書き込んで
```

モデルがファイル書き込みのツール呼び出しを要求し、許可を与えると実際にファイルが作成されます。完了報告が出れば、OpenCode のエージェントループが Sarashina のモデルで動作していることが確認できます。

なお、TUI を介さずにワンショットで確認したい場合は `opencode run` も利用できます。モデルは `--model` オプションで、`プロバイダID/モデルID` の形式で指定します。

```bash
opencode run --standalone --model sarashina/sarashina3.2-mini-thinking "hello.txt というファイルを作成して、「こんにちは」と書き込んで"
```

本稿の執筆環境では、`hello.txt` が作成されたあと、次のような完了報告が返りました。

```text
こんにちは！`hello.txt` というファイルを作成し、「こんにちは」という文字を書き込みました。何か他にお手伝いできることがあれば教えてくださいね。
```

`opencode run` の詳しい使い方は、後半のセクションで改めて扱います。

## 他のコーディングエージェントから利用する

OpenAI 互換の API エンドポイントを設定できるコーディングエージェントであれば、OpenCode 以外からも SarashinaサービスのAPI機能 を利用できます。ここでは、Hermes Agent と Crush を例に接続の設定例を紹介します。Pi も人気のあるコーディングツールですが、API スキーマの関係でSarashina に直接接続することができません。直接接続ができないツールで利用したい場合には、LiteLLM などのプロキシを利用して API 形式を変換してください。

### Hermes Agent

Nous Research が開発するターミナル型のエージェントです。対話形式の `hermes model` コマンドで「Custom endpoint」を選んで登録するか、`~/.hermes/config.yaml` に直接記述します。

```yaml
model:
  default: sarashina3.2-mini-thinking
  provider: custom
  base_url: https://api.sarashina.ai/v1
  key_env: SARASHINA_API_KEY
```

- `key_env`: API キーを保持する環境変数の名前を指定します。キーを直接記述する場合は `api_key` を使います
- `base_url`: `/v1` まで含めて指定してください

以下のようなコマンドを実行し、ファイルが作成されていれば成功です。このコマンドは Hermes Agent v0.22.5 を利用して確認しています。

```sh
hermes chat --oneshot --provider custom -m sarashina3.2-mini-thinking \
  -q "hello.txt というファイルを作成して、「こんにちは」と書き込んで"
```

### Crush

Charm が開発するターミナル型のエージェントです。設定は Bash ベースの設定ファイル `crushrc` に記述します。プロジェクトのルートに `crushrc`(または `.crushrc`)を作成し、次の内容を記述します。

```bash
provider add sarashina --type openai-compat \
  --base-url "https://api.sarashina.ai/v1" \
  --api-key "$SARASHINA_API_KEY"

model add sarashina/sarashina3.2-mini-thinking \
  --name "Sarashina3.2 mini thinking" \
  --context-window 128000 \
  --default-max-tokens 32678
```

設定のポイントは次の通りです。

- `provider add`: `--type` には `openai-compat` を指定します。Crush では OpenAI 自身やそのプロキシ経由の接続は `openai`、OpenAI 以外が提供する OpenAI 互換の API は `openai-compat` と使い分けます。Sarashina は後者に該当します
- `--api-key`: `$SARASHINA_API_KEY` のようにシェルの環境変数を参照できます。crushrc は読み込み時にシェルスクリプトとして評価されるため、設定ファイルにキーの実体を書かずに済みます
- `model add`: モデルごとに表示名やコンテキスト長を登録します。`--default-max-tokens` には、Sarashina の上限である 32678 を指定します

どのプロジェクトからも利用したい場合は、同じ内容を `~/.config/crush/crushrc` に記述します。登録したモデルは TUI のモデル選択から切り替えられるほか、`crush run -m sarashina/sarashina3.2-mini-thinking` のように `プロバイダID/モデルID` の形式で指定して、ワンショットで実行することもできます。

以下のようなコマンドを実行し、ファイルが作成されていれば成功です。このコマンドは Crush v0.98.2 を利用して確認しています。

```sh
crush run -m sarashina/sarashina3.2-mini-thinking \
  "hello.txt というファイルを作成して、「こんにちは」と書き込んで"
```

## 他のモデルのサブエージェントとして Sarashina を利用する

前のセクションでは、OpenCode のメインのモデルを Sarashina に切り替える方法を紹介しました。もう1つの利用形態として、メインのモデルは普段のものを使い続けながら、特定のサブタスクだけを Sarashina に任せる方法があります。日本語文章の校正や要約のような Sarashina が得意な処理を切り出せば、メインのモデルの良さを残したまま Sarashina の強みを取り入れられます。

### OpenCode のカスタムエージェント

OpenCode では、システムプロンプト・利用モデル・権限などをまとめた「エージェント」を定義できます。組み込みエージェントとしては、メインで動作する build や plan、調査向けのサブエージェント explore などが用意されており、独自に作成することもできます。

カスタムエージェントは Markdown ファイルで定義します。プロジェクト単位で使用するならプロジェクトルートの `.opencode/agents/` に、全プロジェクトで共通に使うなら `~/.config/opencode/agents/` に配置します。frontmatter にエージェント設定を書き、本文をシステムプロンプトとして利用します。

frontmatter の主な項目は次の通りです。

- `description`: エージェントの説明です。メインモデルがどのサブエージェントを呼び出すか判断する材料になるため、用途は具体的に記述してください。
- `mode`: `subagent` を指定すると、メインエージェントから呼び出される子セッションとして動作します。サブエージェントは、メインの会話とは切り離された新しいコンテキストで実行されます。
- `model`: このエージェントが使用するモデルを指定します。省略するとメインセッションと同じモデルが使われます。Sarashina を使用したい場合は必ず指定してください。
- `permissions`: 許可する操作を制限します。たとえば、読み取り専用エージェントにしたい場合に利用できます。

### Sarashina のサブエージェントを定義する

例として、日本語の技術記事を校正するサブエージェントを作ります。`.opencode/agents/proofreader.md` を作成し、次の内容を記述します。

```markdown
---
description: Markdown 記事の文章を読みやすさの観点で校正し、ファイルを直接修正する
mode: subagent
model: sarashina/sarashina3.2-mini-thinking
---

あなたは日本語の技術記事の校正者です。指定されたファイルを読み、「読みやすい文体」になるよう表現を校正してください。

校正の基準は次の通りです。

- 一つの文章や段落が長すぎないか
- 回りくどい表現や、過剰な強調表現がないか
- 見出しから内容が予測できる、簡潔でストレートな表現か
- 箇条書きや図表に整理した方が読みやすい箇所がないか

校正は修正案の提示だけでなく、ファイルの書き換えまで行ってください。
```

ポイントを補足します。

`model` には、前のセクションで登録した Sarashina のモデルを指定します。ここでは `sarashina/sarashina3.2-mini-thinking` を使います。

`permissions` は省略しているため、ファイルの編集を含む操作が可能です。このサブエージェントには編集まで任せる想定なので制限はかけていませんが、安全側に倒したい場合は制限を設定できます。

### 動作確認

試しに、回りくどい文体の短文(約100文字)を用意し、`sample.txt` として保存します。

```text
当サービスは、ユーザーがファイルをアップロードすることによって、サーバー上で自動的に処理が行われ、結果が返却されるという仕組みになっておりますので、操作に不慣れな方でも簡単にご利用いただけるものと考えております。
```

サブエージェントを配置したら OpenCode を起動します。メインのモデルは `/models` で選択し直せるので、普段利用している別のプロバイダのモデルに切り替えて試してみます。

メインのエージェントに、サブエージェントの利用を指示します。

```text
sample.txt を proofreader サブエージェントに校正させて
```

メインのモデルが proofreader の呼び出しを開始すると、`description` の内容が判断材料となりサブエージェントが選択されます。校正の実行は Sarashina のモデル上で行われ、TUI ではサブエージェントの起動がツール呼び出しとして表示され、完了するとファイルが実際に修正されます。

実行後の `sample.txt` は次のように書き換えられていました。

```text
当サービスは、ユーザーがファイルをアップロードすると、サーバー上で自動的に処理が行われ、結果が返却される仕組みです。そのため、操作に不慣れな方でも簡単にご利用いただけます。
```

「ことによって」が「と」に、「〜という仕組みになっておりますので」が「仕組みです。そのため」に簡潔化され、長い一文の分割も行われています。定義した校正の基準に沿った修正が、Sarashina のモデルによって適用されたことが確認できます。

このように、エージェントごとにモデルを指定するだけで、メインは既存のモデル、サブタスクの実行は Sarashina、という使い分けが実現できます。

## Claude Code から OpenCode 経由で Sarashina へタスクを委譲する

接続方法の整理で示した通り、Claude Code は Anthropic Messages API でしか通信できないため、SarashinaサービスのAPI機能 に直接接続することはできません。プロトコル変換のプロキシを立てる方法のほかにも、OpenCode へタスクを委譲するという選択肢があります。Claude Code はコマンド実行の機能を持つので、その子プロセスとして OpenCode を起動し、接続済みの Sarashina で処理させる構成です。なお、OpenCode には他のツールから呼び出すためのサーバーモードは存在しないため(本稿執筆時点)、委譲はコマンドのワンショット実行という形になります。ここでは、Claude Code v2.1.312 を利用した方法を紹介します。

### opencode run による非対話実行

委譲に使用するのは `opencode run` です。メッセージを引数に取り、TUI を介さずにエージェントループを実行し、最終的な回答を標準出力に返して終了します。コマンドとして完結するため、Claude Code のような他のツールからそのまま呼び出せます。

```bash
opencode run --standalone --auto -m sarashina/sarashina3.2-mini-thinking "sample.txt を読み、文章を校正してファイルを書き換えて"
```

今回使う主なオプションは次の通りです。

- `-m` / `--model`: 使用するモデルを `プロバイダID/モデルID` の形式で指定します
- `--auto`: 許可が必要な操作を自動で承認します。対話のない呼び出しでは、確認プロンプトで処理が停止しないように付与します
- `--standalone`: バックグラウンドのサービスを使わず、実行のたびに専用のサーバープロセスで動作します。他のツールのセッション内部からの呼び出しでは、素の `opencode run` が失敗する環境があるため、委譲用途では付けておきます

### 委譲手順をスキルとして定義する

Claude Code 側には、どのようなタスクを・どうやって OpenCode に委譲するかを伝える必要があります。ここでは、Claude Code の「スキル」として手順を定義します。スキルは、特定の作業の手順をまとめた Markdown ファイルで、frontmatter の `description` に書いた用途に合致する指示を受け取ると、自動的に適用されます。

`.claude/skills/delegate-to-sarashina/SKILL.md` を作成し、次の内容を記述します。スキルは「スキル名のディレクトリに `SKILL.md` を置く」形で配置し、ディレクトリ名と frontmatter の `name` は一致させます。

```markdown
---
name: delegate-to-sarashina
description: 日本語文章の校正・要約・推敲など、日本語処理の得意なモデルに任せたいタスクを、OpenCode 経由で Sarashina に委譲する。「Sarashina を利用して」という指示で使用する。
---

日本語文章の校正や要約などのタスクは、次のコマンドで OpenCode 経由の Sarashina に委譲する。

opencode run --standalone --auto -m sarashina/sarashina3.2-mini-thinking "<指示>"

結果はコマンドの標準出力として返る。ファイルの修正を伴う場合は、実行後に差分を確認すること。

委譲はワンショットの子プロセス実行で、Claude Code の会話コンテキストは共有されない。指示の中に対象ファイルや要件を具体的に含めること。
```

frontmatter の `description` は、受け取った指示にこのスキルを適用するかどうかの判断材料になります。校正や要約のような対象タスクと、「Sarashina を利用して」のような起動の合図を具体的に書いておくのがポイントです。

子プロセスの `opencode run` は、Claude Code の環境変数を引き継いで動きます。そのため、Claude Code も環境変数 `SARASHINA_API_KEY` を設定したターミナルから起動してください。

### 動作確認

前のセクションと同じ `sample.txt`(校正前の回りくどい短文)を使って、委譲の流れを確認します。Claude Code を起動し、次のように指示します。

```text
sample.txt を Sarashina に委譲して校正して
```

スキルが適用され、定義した手順に従って Claude Code はコマンド実行ツールで `opencode run` を呼び出します。実行中の出力には、OpenCode 側のツール呼び出し(ファイルの読み取り・編集)の様子と、Sarashina のモデルによる最終回答が標準出力に流れ、Claude Code がその出力を受け取って結果を報告します。

本稿の執筆環境では、実行後の `sample.txt` は次のように書き換えられていました。

```text
当サービスでは、ユーザーがファイルをアップロードすると、サーバー上で自動的に処理が行われ、結果が返却されます。そのため、操作に不慣れな方でも簡単にご利用いただけます。
```

これで、Claude Code を普段のエージェントとして使いながら、日本語処理の得意なタスクだけを Sarashina に任せる構成が完成です。

## おわりに

本稿では、コーディングエージェントから SarashinaサービスのAPI機能 を利用する方法を紹介しました。OpenCode からの直接接続を軸に、メインモデルとして使う方法、他のモデルのサブエージェントとして組み込む方法、Claude Code からタスクを委譲する方法の3つの利用形態を扱いました。接続は設定ファイルへの記述だけで完結するため、既存の環境にも手軽に組み込めます。

すべての処理でモデルを切り替える必要はありません。日本語文章の校正や要約のように Sarashina が得意とする処理だけを切り出して、サブエージェントとして任せる構成は、普段の開発環境を保ったまま試せる入り口になります。まずは1つのサブタスクからお試しください。

API 機能の詳細と API キーの発行については、[sarashina.ai](https://sarashina.ai/#japanese) を参照してください。
