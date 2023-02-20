FROM python:3.8-slim

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY . .

CMD ["python", "manage.py", "runserver"]