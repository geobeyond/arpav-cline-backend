FROM python:3.10

# Install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    apt-utils \
    tini

# download poetry
RUN curl --silent --show-error --location \
    https://install.python-poetry.org > /opt/install-poetry.py

# Create a normal non-root user so that we can use it to run
RUN useradd --create-home appuser

# Compile python stuff to bytecode to improve startup times
RUN python -c "import compileall; compileall.compile_path(maxlevels=10)"

USER appuser

# create relevant directories and install poetry
RUN mkdir /home/appuser/app  && \
    mkdir /home/appuser/data && \
    python opt/install-poetry.py --yes --version 1.7.1

ENV PATH="$PATH:/home/appuser/.local/bin" \
    PYTHONUNBUFFERED=1 \
    # This allows us to get traces whenever some C code segfaults
    PYTHONFAULTHANDLER=1

WORKDIR /home/appuser/app

COPY --chown=appuser:appuser pyproject.toml poetry.lock ./

RUN poetry install --no-root --only main

EXPOSE 8000

ARG GIT_COMMIT
ENV GIT_COMMIT=$GIT_COMMIT \
  ARPAV_PPCV__BIND_HOST=0.0.0.0

# Now install our code
COPY --chown=appuser:appuser . .
RUN poetry install --only main

# Write git commit identifier into the image
RUN echo $GIT_COMMIT > /home/appuser/git-commit.txt

# Compile python stuff to bytecode to improve startup times
RUN poetry run python -c "import compileall; compileall.compile_path(maxlevels=10)"

# use tini as the init process
ENTRYPOINT ["tini", "-g", "--", "poetry", "run", "arpav-ppcv"]

CMD ["run-server"]
