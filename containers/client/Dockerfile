FROM python:3.9-buster

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY ./src /app/src
EXPOSE ${RPC_PORT}

CMD python -m src.client