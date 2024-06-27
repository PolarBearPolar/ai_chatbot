import logging
import os
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage, MessageRole

class Config:

    # Chatbot API configuration
    API_HOST = "0.0.0.0"
    API_PORT = 8001

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
    LLM = os.environ.get("OLLAMA_MODEL")
    LLM_URL = f"http://ollama:{os.environ.get('OLLAMA_PORT')}"
    LLM_REQUEST_TIMEOUT = 20000
    LLM_TEMPERATURE = 0.4
    SIMILARITY_TOP_KEY = 10

    # Promt template configuration
    SYSTEM_ROLE = """\
    You are a helpful, respectful psychological assistant that helps people solve the issues related to their emotional state. \
    Answer as helpfully as possible using the context provided.
    Your answers should only answer the query once and not have text afer the answer is done.
    In case you do not know the answer just say that you do not \
    know the answer and do not say anything else.
    """
    TEXT_QA_TEMPLATE_STR = """\
    Context information is below.
    ---------------------
    {context_str}
    ---------------------
    Answer the query using the context information provided and stick to the topic of psychology. Use your prior knowledge if required. \
    In case the answer is not mentioned in the context or the context is not related to the query, \
    just say that you do not know the answer and do not say anything else.
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
    solve the issues related to their emotional state. Use only the existing \
    answer and the new context to generate the refined answer. In case the answer \
    is not mentioned in the new context or the new context is not related to the query, \
    use the original answer as the refined answer.
    Refined Answer: \
    """
    TEXT_QA_TEMPLATE = ChatPromptTemplate(
        [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    SYSTEM_ROLE
                ),
            ),
            ChatMessage(role=MessageRole.USER, content=TEXT_QA_TEMPLATE_STR),
        ]
    )
    REFINE_TEMPLATE = ChatPromptTemplate(
        [
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    SYSTEM_ROLE
                ),
            ),
            ChatMessage(role=MessageRole.USER, content=REFINE_TEMPLATE_STR),
        ]
    )
