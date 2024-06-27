#!/bin/bash
echo "Checking if the backend is up and running..."
backend_status=1
while [ $backend_status -ne 0 ]
do
	nc -z backend $BACKEND_PORT
	backend_status=$?
	sleep 5
done
echo "The backend is running..."

echo "Launching the frontend..."
streamlit run app.py
