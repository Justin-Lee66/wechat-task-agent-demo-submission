# Decisions

## Use Text Fixtures by Default

The take-home should be runnable by a reviewer without secrets or network calls. Text fixtures provide deterministic behavior and make tests stable.

## Keep Screenshots as Fixtures

Screenshots are included so optional `llm_vision` mode can be demonstrated without pretending to be a real WeChat integration.

## SQLite Over an ORM

SQLite plus explicit SQL keeps persistence transparent. The schema mirrors the assignment rubric and avoids framework weight.

## Conservative Normalization

Unclear due phrases such as `开盘前` and `day of` are unresolved and marked `needs_review`. The system should surface ambiguity rather than invent deadlines.

## No Hermes Runtime Dependency

Hermes-style scheduling is a plausible production extension, but this repo remains independent for local review.

