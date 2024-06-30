FROM ubuntu:22.04

EXPOSE 8000

ARG BACKEND_PORT
ENV BACKEND_PORT=$BACKEND_PORT

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
