FROM python:3.10-windowsservercore

WORKDIR /app

RUN python -m pip install --upgrade pip

COPY . .

CMD ["python", "-m", "gbill"]