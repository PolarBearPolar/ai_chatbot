FROM ubuntu:20.04

EXPOSE 11434

ARG OLLAMA_MODEL
ENV OLLAMA_MODEL=$OLLAMA_MODEL
ENV OLLAMA_HOST=0.0.0.0

RUN apt-get update && apt-get install -y curl
RUN curl -fsSL https://ollama.com/install.sh|sh

WORKDIR /home

COPY create_custom_llm.sh .
COPY Modelfile .

RUN chmod +x create_custom_llm.sh
RUN ./create_custom_llm.sh

ENTRYPOINT ["ollama", "serve"]
