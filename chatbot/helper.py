import weaviate
import logging
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from config import Config


def getLlm() -> Ollama:
    llm = Ollama(
        model=Config.LLM, 
        base_url=Config.LLM_URL,
        request_timeout=Config.LLM_REQUEST_TIMEOUT, 
        temperature=Config.LLM_TEMPERATURE
    )
    return llm


def getEmbeddingModdel() -> LangchainEmbedding:
    embeddingModel = LangchainEmbedding(
        HuggingFaceEmbeddings(model_name=Config.EMBEDDING_MODEL)
    )
    return embeddingModel


def configureSettings() -> "Settings":
    Settings.llm = getLlm()
    Settings.embed_model = getEmbeddingModdel()
    Settings.chunk_size = Config.EMBEDDING_CHUNK_SIZE
    Settings.chunk_overlap = Config.EMBEDDING_CHUNK_OVERLAP
    return Settings


def createWeaviateClient() -> weaviate.Client:
    client = weaviate.Client(Config.WEAVIATE_URL)
    if not client.schema.exists(class_name=Config.DOCUMENT_CLASS_NAME):
       client.schema.create(Config.WEAVIATE_SCHEMA)
    return client


def getFileLogger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(Config.LOG_LEVEL)
    formatter = logging.Formatter(Config.LOG_FORMAT)
    fileHandler = logging.FileHandler(Config.LOG_FILE, mode="a")
    fileHandler.setLevel(Config.LOG_LEVEL)
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    return logger
