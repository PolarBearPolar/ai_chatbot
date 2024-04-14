#!/bin/bash
echo "Checking if ollama is up and running..."
ollama_status=1
while [ $ollama_status -ne 0 ]
do
	nc -z ollama $OLLAMA_PORT
	ollama_status=$?
	sleep 5
done
echo "Ollama is running..."

echo "Checking if the vector database is up and running..."
vector_database_status=1
while [ $vector_database_status -ne 0 ]
do
	nc -z vector_database $VECTOR_DATABASE_PORT
	vector_database_status=$?
	sleep 5
done
echo "The vector database is running..."

echo "Launching the chatbot... Have fun :)"
python3 main.py
