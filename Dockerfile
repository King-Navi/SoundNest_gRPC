FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

COPY . /app

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY . /app

EXPOSE 50051

CMD ["poetry", "run", "python", "-u", "src/server.py"]

# Si agregas compilaciones C (como numpy, pandas), instala:
# RUN apt-get update && apt-get install -y build-essential
# Si usas node/npm (para frontend), puedes agregar:
# RUN apt-get update && apt-get install -y nodejs npm