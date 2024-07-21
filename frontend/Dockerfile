FROM ubuntu:22.04

EXPOSE 8501

ARG BACKEND_PORT
ARG DEFAULT_LANGUAGE
ENV BACKEND_PORT=$BACKEND_PORT
ENV DEFAULT_LANGUAGE=$DEFAULT_LANGUAGE

RUN mkdir frontend
WORKDIR ./frontend

COPY ./requirements.txt .

RUN apt-get update && \
	apt-get upgrade -y && \
	apt-get install -y netcat && \
	apt-get install -y python3 && \
	apt-get install -y python3-pip

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

ENTRYPOINT ["./run_frontend.sh"]
