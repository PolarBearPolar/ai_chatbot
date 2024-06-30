# AI Psychological Assistant 🤖
## Introduction 
This is an AI powered psychological assistant application. The assistant specilizes in managing stress, depression, anxiety, fear, and apathy.  
  
👉 The application is easy to navigate and use.  
  
👉 You can have multiple chats with the assistant and all of them will be stored (persisted) in a PostgreSQL database. In case you want to remove any chat from your chat history, you can do it by simply clicking the **Delete chat** button.  
  
👉 The project is split into multiple components/services. The service that is responsible for large language model (LLM) interaction allows to include external data (external for the LLM) when generating answers to your queries (it is called Retrieval-Augmented Generation (RAG)). 'External', in this context, means the information that the LLM is not familar with and has not been trained on. In our case, this 'external' information is the psychology-related data stored in txt format that I considered to be the most relevant to the topic of dealing with stress, depression, anxiety, fear, and apathy. This data will be called RAG data throughout this description.  
  
👉 RAG data is processed (transformed into numerical vectors) and stored/persisted in a Weaviate vector database.
  
## User Interface Layout 🖼️
Here is a basic description of the user interface of the application.
![image](https://github.com/PolarBearPolar/ai_chatbot/assets/88388315/d896f639-089a-46cc-8f9a-4ecefca705d9)
1. User information form.
2. Chat history. Click on the **New chat+** button to create a new chat with the assistant. Click on other chat buttons to switch between the chats you have already initiated with the assitant.
3. A short description of the assistant. The description area contains the **Delete chat** button. It is active only when a chat is selected. If you click on it, the opened chat will be deleted.
4. The chat area. Write your question/queries into the query bar and send them to the assistant to have a conversation.
## Application Architecture Design 🛠️
Here is the project architecture.
![image](https://github.com/PolarBearPolar/ai_chatbot/assets/88388315/95e0f823-2187-4c5a-aec5-d546fbdc2f9f)
## How to Use Application 🚀
The initial idea of this project was to create a local chatbot API using an open-source large language model (LLM). However, due to insufficient resources, I had to use a 3rd party service to interact with the LLM. The LLM used in this project is the open-source LLM called Llama3 by Meta. So in order to use this model, go to [together.ai](https://www.together.ai/) and sign in. You will be given an API key. Copy it because you will need it later on.
- Make sure you have Docker installed.
- Make sure ports **8501**, **8000**, **8001**, **5432**, **8080** are not used on your local machine.
- Clone the repository to any directory on your local machine
- **cd** into the directory that contains the cloned repo.
- Open the **docker-compose.yml** file and replace the *LLM_API_KEY: '\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*\*'* with *LLM_API_KEY: your api key that you copied*.
- Run the following command there (Linux Docker command example)
```
sudo docker compose -f docker-compose.yml up
```
- Wait until all the containers are up and running
- In order to use RAG data, go to the **./chatbot/data directory**. Keep the example files or replace them with your own files if you want to chat with your data files. Run the command below to ingest RAG data (to process it and save it to the vector database):
```
sudo docker exec chatbot python3 ingest.py
```
- You may start using the application.
-   
If you ever need to delete your RAG data from the vector database, run the following command:
```
sudo docker exec chatbot python3 clear_vector_db.py
```
If you wish to configure the chatbot component of this application to your needs, you can start from changing the configurations in the **docker-compose.yml** file or the **./chatbot/config.py** file. In case you want to use Ollama or OpenAI API, change the *getLlm()* method in the **./chatbot/helper.py** file accordingly.
