#!/bin/bash
echo "Creating a custom $OLLAMA_MODEL model..."
echo "FROM $OLLAMA_MODEL" >> ./Modelfile
create_status=1
while [ $create_status -ne 0 ]
do
	ollama serve &
	ollama create psychological-assistant-model -f ./Modelfile
	create_status=$?
	echo pull_status
	sleep 5
done
echo "The psychological-assistant-model has been successfully created..."
