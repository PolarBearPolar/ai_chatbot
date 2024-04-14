FROM ubuntu:20.04

EXPOSE 11434

ARG OLLAMA_MODEL
ENV OLLAMA_MODEL=$OLLAMA_MODEL
ENV OLLAMA_HOST=0.0.0.0

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://ollama.com/install.sh|sh

WORKDIR /home

COPY pull_llm.sh .

RUN chmod +x pull_llm.sh
RUN ./pull_llm.sh

ENTRYPOINT ["ollama", "serve"]
