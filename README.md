# TypeSafe AI API Example

A small semantic search example that uses the TypeSafe SDK to find the FAQ
entry that best answers a natural-language question.

## Prerequisites

- Python 3.14 or later
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A TypeSafe API key from the [TypeSafe console](https://console.typesafe.ai/)

## Setup

Install the project dependencies:

```sh
uv sync
```

Create a `.env` file in the project root:

```dotenv
TYPESAFE_API_KEY=your-api-key
```

Do not commit the `.env` file or your API key to source control.

## Run

Load the variables from `.env` and run the example:

```sh
uv run --env-file .env main.py "Why won't my payment provider connect?"
```

The script uses a `Choice` question to rank the FAQ entries and a `Noul`
question to determine whether any entry answers the query. It prints the best
match, answer relevance, choice confidence, and complete ranking.

Try queries such as:

```sh
uv run --env-file .env main.py "How do I recover my account?"
uv run --env-file .env main.py "Can I get a refund when I cancel?"
uv run --env-file .env main.py "What is the weather today?"
```
