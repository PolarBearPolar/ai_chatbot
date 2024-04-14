#!/bin/bash
echo "Pulling the $OLLAMA_MODEL image..."
pull_status=1
while [ $pull_status -ne 0 ]
do
	ollama serve &
	ollama pull $OLLAMA_MODEL
	pull_status=$?
	echo pull_status
	sleep 5
done
echo "The $OLLAMA_MODEL image has been pulled..."
