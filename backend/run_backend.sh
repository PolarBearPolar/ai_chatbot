#!/bin/bash
echo "Checking if the chatbot is up and running..."
chatbot_status=1
while [ $chatbot_status -ne 0 ]
do
	nc -z chatbot $CHATBOT_PORT
	chatbot_status=$?
	sleep 5
done
echo "The chatbot is running..."

echo "Checking if the database is up and running..."
database_status=1
while [ $database_status -ne 0 ]
do
	nc -z database $POSTGRES_PORT
	database_status=$?
	sleep 5
done
echo "The database is running..."

echo "Launching the backend..."
python3 main.py
