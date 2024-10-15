FROM python:3.12-alpine

WORKDIR /app

COPY poetry.lock pyproject.toml ./

RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install --no-cache-dir poetry==1.8.3

RUN poetry config virtualenvs.create false
RUN poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD ["tire_bot"]
