# 🤖 AI Psychological Assistant 👩‍⚕️
## Introduction 
This is an AI powered psychological assistant application. The assistant specilizes in managing stress, depression, anxiety, fear, and apathy.  
  
👉 The application is easy to navigate and use.  

👉 The application supports 3 languages - English, Serbia, Russian.  
  
👉 You can have multiple chats with the assistant and all of them will be stored/persisted in a PostgreSQL database. In case you want to remove any chat from your chat history, you can do it by simply clicking the **Delete chat** button.  

👉 The assistant keeps track of a conversation history within each chat so that you can have a human-like conversation with it. 

👉 When you ask the assistant questions, it classifies your questions to topics (stress, depression, anxiety, fear, apathy, or other). When answering the questions, the assistant looks for relevant external data provided to it by the user/admin (e.g. documents on how to deal with stress of your choosing). When a question is classified as 'other', the assistant answers the question based on its own knowledge base. 
  
The project is split into multiple components/services. The service that is responsible for large language model (LLM) interaction allows to include external data (external for the LLM) when generating answers to your queries. This is called Retrieval-Augmented Generation (RAG). 'External', in this context, means the information that the LLM is not familar with and has not been trained on. In our case, this 'external' information is the psychology-related data stored in txt format that I considered to be the most relevant to the topic of dealing with stress, depression, anxiety, fear, and apathy. This data will be called RAG data throughout this description. RAG data is processed (transformed into numerical vectors) and stored/persisted in a Weaviate vector database.
  
## User Interface Layout 🖼️
Here is a basic description of the user interface of the application.
### Welcoming Page
![image](https://github.com/user-attachments/assets/3c58addb-d80f-4440-bfa9-c4430930b03c)
You can choose a language and enter your credentials here to log into the application
### Main Page
![image](https://github.com/user-attachments/assets/b7acf416-7a44-406b-8994-f3d156820557)
1. User information form.
2. Chat history. Click on chat buttons to switch between the chats you have already initiated with the assitant.
3. A short description of the assistant. The description area contains the **START NEW CHAT** and **DELETE CURRENT CHAT** buttons. You can click on them, to pen or delete a chat.
4. The chat area. Write your question/queries into the query bar and send them to the assistant to start a conversation.
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
- Run the following command (Linux Docker command example)
```
sudo docker compose -f docker-compose.yml up
```
- Wait until all the containers are up and running
- In order to use RAG data, go to the **./chatbot/data** directory
- Move the example files to another directory
- Copy one of the example files back in the **./chatbot/data** directory and run the command below to ingest RAG data (to process it and save it to the vector database). For example, the **managing_fear.txt** file -> topic **fear**:
```
sudo docker exec chatbot python3 ingest.py fear
```
- Repeat the copying step for the remaining files one at a time. Do not forget to pass the relevant topic argument to the command. If you want to, you can use your txt files instead.
- You may start using the application now  

If you ever need to delete your RAG data from the vector database, run the following command:
```
sudo docker exec chatbot python3 clear_vector_db.py
```
If you wish to configure the chatbot component of this application to your needs, you can start from changing the configurations in the **docker-compose.yml** file or the **./chatbot/config.py** file. In case you want to use Ollama or OpenAI API, change the *getLlm()* method in the **./chatbot/helper.py** file accordingly.
