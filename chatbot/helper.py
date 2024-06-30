import weaviate
from llama_index.llms.together import TogetherLLM
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from config import Config


def getLlm() -> TogetherLLM:
    llm = TogetherLLM(
        model=Config.LLM, 
        api_key=Config.LLM_API_KEY,
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
