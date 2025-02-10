# Use Poetry for Python dependency management

## Context and Problem Statement

We want to use a tool to both manage project Python dependencies and packaging. Given the number of alternatives that
currently exist and the project requirements, which would be an appropriate choice?


## Considered Options

- [poetry](https://python-poetry.org/)
- [pdm](https://pdm-project.org/latest/)
- [pipenv](https://pipenv.pypa.io/en/latest/)
- [rye](https://rye-up.com/)


## Decision Outcome

Chosen option: "poetry", because it meets the needs of the project and introduces minimal friction


### Consequences

- Good, because it is already known by the project development team
- Good, because it covers all relevant use cases related to development and deployment for the project:
  - uses pinned versions for dependencies
  - allows defining user scripts, for building custom commands
  - specify development-only dependencies, which can be kept off the docker image
  - allows installing only dependencies if needed, which is good for preserving the docker cache


### pdm

- Good, because it covers project use cases
- Bad, because the development team does not have experience using it


### pipenv

- Good, because it covers project use cases
- Bad, because the development team does not have experience using it


### rye

- Good, because it covers project use cases
- Bad, because the development team does not have experience using it
- Bad, because it is a very new tool, which may not be as stable as desired for the current project
