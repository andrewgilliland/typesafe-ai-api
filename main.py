import argparse

from typesafe_sdk import (
    Choice,
    Noul,
    NoulCriteria,
    TypeSafeClient,
)

DOCUMENTS = {
    "billing": "Update a credit card or investigate duplicate charges.",
    "stripe": "Troubleshoot connecting and synchronizing a Stripe account.",
    "password": "Reset a forgotten password or recover an account.",
    "cancel": "Cancel a subscription and review the refund policy.",
}
MINIMUM_RELEVANCE = 0.7


def search(query: str) -> None:
    with TypeSafeClient() as client:
        response = client.system_one(
            state={"query": query, "documents": DOCUMENTS},
            questions={
                "best_match": Choice(
                    instructions=(
                        "Which entry in `documents` most directly answers `query`? "
                        "Return its key."
                    ),
                    criteria={document_id: None for document_id in DOCUMENTS},
                ),
                "has_answer": Noul(
                    instructions=(
                        "Does any entry in `documents` meaningfully answer `query`?"
                    ),
                    criteria=NoulCriteria(
                        true="At least one document directly addresses the query",
                        false="None of the documents answer the query",
                    ),
                ),
            },
        )

    match = response.choices["best_match"]
    relevance = response.nouls["has_answer"].noul

    print(f"Query: {query}")
    print(f"Answer relevance: {relevance:.2f}")

    if relevance < MINIMUM_RELEVANCE:
        print("No sufficiently relevant result.")
        return

    print(f"Best match: {match.choice}")
    print(f"Result: {DOCUMENTS[match.choice]}")
    print(f"Choice confidence: {match.confidence:.2f}")

    print("\nRanking:")
    for document_id, probability in sorted(
        match.probabilities.items(), key=lambda item: item[1], reverse=True
    ):
        print(f"  {document_id}: {probability:.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Search the example FAQ by meaning.")
    parser.add_argument("query", help="A natural-language question")
    args = parser.parse_args()
    search(args.query)


if __name__ == "__main__":
    main()
