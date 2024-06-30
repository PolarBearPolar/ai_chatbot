FROM ubuntu:22.04

EXPOSE 8001

ARG LLM
ARG LLM_API_KEY
ARG LLM_TEMPERATURE
ARG VECTOR_DATABASE_PORT
ENV LLM=$LLM
ENV LLM_API_KEY=$LLM_API_KEY
ENV LLM_TEMPERATURE=$LLM_TEMPERATURE
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
