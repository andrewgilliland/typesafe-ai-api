# TypeSafe AI API Example

A small Python example that uses the TypeSafe SDK to classify a customer
support ticket by department, frustration, and urgency.

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
uv run --env-file .env main.py
```

The script prints the selected department, frustration score, and urgency
score returned by TypeSafe.
