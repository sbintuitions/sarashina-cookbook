<p align="center">
  <a href="README.md">日本語</a> | <b>English</b>
</p>

# Sarashina Cookbook

The Sarashina Cookbook is a repository of code and guides for building applications with the Sarashina API.
It aims to be a place where those interested in the Sarashina API can explore how it can be used and find sample code that is easy to adapt into their own projects.

## Sarashina API

To run the recipes in this cookbook, you need a Sarashina API key. You can get one for free at [sarashina.ai](https://sarashina.ai/#japanese).

## Setup

```bash
git clone https://github.com/sbintuitions/sarashina-cookbook.git
cd sarashina-cookbook
uv sync --locked
```

Copy `.env.sample` to create a `.env` file and set your API key.

```
SARASHINA_API_KEY=xxx
```

If you are new to the Sarashina API, we recommend starting with the quickstart in the [official API documentation](https://docs.sarashina.ai) to learn the basics of how to call the API.

## Recipes

### RAG (Retrieval-Augmented Generation)

- [Example of building a RAG system with Sarashina]()
- [Improving RAG Retrieval Accuracy with Sarashina (1/2)](https://www.sbintuitions.co.jp/blog/entry/2026/11/12/170000)

### Coding Agents

- [Using Sarashina with Coding Agents: OpenCode, Hermes Agent, and Crush Integrations and Use as a Subagent](https://www.sbintuitions.co.jp/blog/entry/2026/11/06/100000)

## Links

- [Sarashina API documentation](https://docs.sarashina.ai)
- [Sarashina official website](https://sarashina.ai)
- [SB Intuitions official website](https://www.sbintuitions.co.jp/en/)

## License

This repository is released under the MIT License. See [LICENSE](LICENSE) for details.
