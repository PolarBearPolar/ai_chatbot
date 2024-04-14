FROM ubuntu:22.04

EXPOSE 8000

ARG OLLAMA_MODEL
ARG OLLAMA_PORT
ARG VECTOR_DATABASE_PORT
ENV OLLAMA_MODEL=$OLLAMA_MODEL
ENV OLLAMA_PORT=$OLLAMA_PORT
ENV VECTOR_DATABASE_PORT=$VECTOR_DATABASE_PORT

RUN mkdir chatbot
WORKDIR ./chatbot

COPY ./requirements.txt .

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y netcat && \
	apt-get install -y python3 && \
	apt-get install -y python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./run_chatbot.sh"]
