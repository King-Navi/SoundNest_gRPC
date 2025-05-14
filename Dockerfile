FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get purge -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

COPY . /app

EXPOSE 50051

CMD ["poetry", "run", "python", "-u", "src/server.py"]

# Si agregas compilaciones C (como numpy, pandas), instala:
# RUN apt-get update && apt-get install -y build-essential
# Si usas node/npm (para frontend), puedes agregar:
# RUN apt-get update && apt-get install -y nodejs npm