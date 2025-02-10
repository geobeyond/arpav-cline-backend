# Use ruff for Python code linting and formatting

## Context and Problem Statement

We want to ensure committed code is checked for common errors and is formatted with a standard style. Given the
number of alternatives that currently exist and the project requirements, which would be an appropriate choice?


## Considered Options

* [ruff](https://docs.astral.sh/ruff/)
* [flake8](https://flake8.pycqa.org/en/latest/) + [black](https://black.readthedocs.io/en/stable/index.html)


## Decision Outcome

Chosen option: "ruff", because it does both linting and formatting, supports all relevant features of the
"flake8 + black" option and is fast to operate

### Consequences

* Good, because it is easy to install and setup
* Good, because it is fast to execute
* Good, because it is configurable
* Good, because it contains a large number of built-in rules
