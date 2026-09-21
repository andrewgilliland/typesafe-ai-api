# Domain Docs

This is a single-context repository.

## Before exploring

Read these documents when they exist:

- `CONTEXT.md` at the repository root
- Relevant ADRs under `docs/adr/`

If these files do not exist, proceed silently. Do not suggest creating them upfront. The domain-modeling skill creates them lazily when domain terms or architectural decisions need to be recorded.

## Use the glossary vocabulary

When naming a domain concept in an issue, refactor proposal, hypothesis, or test, use the term defined in `CONTEXT.md`. If the needed concept is not defined there, treat that as a signal to reconsider the terminology or record the gap through domain modeling.

## Flag ADR conflicts

If proposed work contradicts an existing ADR, surface the conflict explicitly rather than silently overriding it.
