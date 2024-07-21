import logging
import os
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole

class Config:

    def __getFloatLlmTemperature(strTemp: str=None) -> float:
        temp = 0.5
        try:
            temp = float(strTemp)
            if temp < 0.0 or temp > 1.0:
                raise ValueError("The temperature parameter value must be within 0.0-1.0.")
        except:
            pass
        return temp

    # Chatbot API configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8001
    API_DEFAULT_LANGUAGE = "en"

    # Role constants
    ROLE_ASSISTANT = "ASSISTANT"
    ROLE_USER = "USER"

    # Logging configuration
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
    LOG_FILE = "log.log"

    # Vector database configuration
    WEAVIATE_URL = f"http://vector_database:{os.environ.get('VECTOR_DATABASE_PORT')}"
    WEAVIATE_SCHEMA = {
        "classes": [
            {
                "class": "Document",
                "description": "A document class",
                "properties": [
                    {
                        "name": "content",
                        "dataType": ["text"],
                        "description": "Text content for the document",
                    },
                ],
            },
        ],
    }
    DOCUMENT_CLASS_NAME = "Document"
    DOCUMENT_CONTENT_PROPERTY = "content"
    # Document directory that is used
    # to load documents into vector database
    DOCUMENTS_DIRECTORY = "data"

    # Embedding model configuration
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    EMBEDDING_CHUNK_SIZE = 1000
    EMBEDDING_CHUNK_OVERLAP = 20

    # Large language model configuration
    LLM = os.environ.get("LLM")
    LLM_API_KEY=os.environ.get("LLM_API_KEY")
    LLM_REQUEST_TIMEOUT = 20000
    LLM_TEMPERATURE = __getFloatLlmTemperature(os.environ.get("LLM_TEMPERATURE"))
    SIMILARITY_TOP_KEY = 5

    # Promt template configuration
    SYSTEM_ROLE = {
        "en": "You are a helpful psychological assistant that helps people solve different types of issues related to their emotional state. You support people through life's challenges. You specialize in managing stress, depression, anxiety, fear, and apathy. Your goal is to offer personalized advice to users. Your name is AI Psychological Assistant.", 
        "sr": "Vi ste od pomoći psihološki asistent koji pomaže ljudima da reše različite vrste pitanja vezanih za njihovo emocionalno stanje. Podržavate ljude kroz životne izazove. Specijalizovani ste za upravljanje stresom, depresijom, anksioznošću, strahom i apatijom. Vaš cilj je da ponudite personalizovane savete korisnicima. Vaše ime je AI psihološki asistent. Sve svoje odgovore dajte samo na srpskom jeziku.",
        "ru": "Вы полезный психологический помощник, который помогает людям решать различные проблемы, связанные с их эмоциональным состоянием. Вы поддерживаете людей в жизненных трудностях. Вы специализируетесь на управлении стрессом, депрессией, тревогой, страхом и апатией. Ваша цель — предложить пользователям персонализированные советы. Вас зовут ИИ психологический помощник. Давайте все ответы только на русском языке."
    }
    TEXT_QA_TEMPLATE_STR = """\
    Context information is below.
    ---------------------
    {context_str}
    ---------------------
    Answer the query using the context information provided and stick to the topic of psychology. Use your prior knowledge if required. \
    Do not use the phrase 'Based on the context provided' \
    when giving an answer.
    Query: {query_str}
    Answer: \
    """
    REFINE_TEMPLATE_STR = """\
    The original query is as follows: {query_str}
    We have provided an existing answer: {existing_answer}
    We have the opportunity to refine the existing answer \
    (only if needed) with some more context below.
    ------------
    {context_msg}
    ------------
    Given the new context, try to refine the original answer to better \
    answer the query, keeping in mind that you a psychological assistant that helps people \
    solve the issues related to their emotional state. In case the answer \
    is not mentioned in the new context or the new context is not related to the query, \
    use the original answer as the refined answer. Do not use the phrase 'Based on the context provided' \
    when giving an answer.
    Refined Answer: \
    """
    TEXT_QA_TEMPLATE = [
            ChatMessage(
                role=MessageRole.USER, 
                content=TEXT_QA_TEMPLATE_STR
            ),
        ]
    REFINE_TEMPLATE = [
            ChatMessage(
                role=MessageRole.USER, 
                content=REFINE_TEMPLATE_STR
            ),
        ]

