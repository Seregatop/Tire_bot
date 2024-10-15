FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev
RUN pip install --no-cache-dir poetry==1.8.3

COPY . .

RUN poetry config virtualenvs.create false
RUN poetry install

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "poetry run tire-bot"]