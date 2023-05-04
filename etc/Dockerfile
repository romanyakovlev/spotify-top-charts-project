FROM python:3.9

WORKDIR /app

COPY requirements.txt requirements.txt
COPY ./flows ./flows
COPY ./pyspark_jobs ./pyspark_jobs

RUN pip install -r requirements.txt
