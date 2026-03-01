FROM python:3.13.10-slim AS runtime
# We set the path to include the app root and the submodule folder
ENV PYTHONPATH="/app:/app/dynamiq"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV RUNTIME_PACKAGES="git curl make"
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.3
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH=${POETRY_HOME}/bin:${PATH}

# Install system basics
RUN apt-get update && apt-get install -y $RUNTIME_PACKAGES build-essential
RUN curl -sSL https://install.python-poetry.org | python3 - --yes

WORKDIR /app

# --- CRITICAL: Copy these from the submodule so Poetry can run ---
COPY ./dynamiq/pyproject.toml /app/pyproject.toml
COPY ./dynamiq/poetry.lock* /app/poetry.lock*
COPY ./dynamiq/Makefile /app/Makefile

# Install dependencies defined in Dynamiq
RUN poetry install --no-root

FROM runtime AS develop

# Copy the actual library code from the submodule
COPY ./dynamiq/dynamiq /app/dynamiq/dynamiq

# Copy your specific application code from your docker folder
COPY ./docker/main.py /app/main.py

# Upgrade cryptography and pyOpenSSL for Python 3.13 compatibility
RUN pip install --upgrade cryptography>=44.0.0 pyOpenSSL>=25.0.0

CMD ["python", "main.py"]
