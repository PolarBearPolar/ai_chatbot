FROM ubuntu:22.04

EXPOSE 8000

ARG CHATBOT_PORT
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_PORT
ARG POSTGRES_DB
ARG IS_RAG_USED
ENV CHATBOT_PORT=$CHATBOT_PORT
ENV POSTGRES_USER=$POSTGRES_USER
ENV POSTGRES_PASSWORD=$POSTGRES_PASSWORD
ENV POSTGRES_PORT=$POSTGRES_PORT
ENV POSTGRES_DB=$POSTGRES_DB
ENV IS_RAG_USED=$IS_RAG_USED

RUN mkdir backend
WORKDIR ./backend

COPY ./requirements.txt .

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y netcat && \
	apt-get install -y python3 && \
	apt-get install -y python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./run_backend.sh"]
