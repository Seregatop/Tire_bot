FROM python:3.12-alpine

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip \
    && python -m pip install poetry==1.8.3

RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi \
    && rm -rf $(poetry config cache-dir)/{cache,artifacts}

COPY . .

CMD ["sh", "tire_bot"]