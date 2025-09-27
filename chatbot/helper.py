import weaviate
import re
from llama_index.llms.together import TogetherLLM
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.llms import ChatMessage
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from weaviate.classes.query import Filter
from config import Config
from model import ChatElement, QueryResponseElement
from contextlib import asynccontextmanager


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
    client = weaviate.connect_to_local(
        host=Config.WEAVIATE_HOST,
        port=Config.WEAVIATE_PORT   
    )
    if not client.collections.exists(Config.DOCUMENT_CLASS_NAME):
        client.collections.create(
            name=Config.WEAVIATE_SCHEMA["classes"][0]["class"],
            description=Config.WEAVIATE_SCHEMA["classes"][0]["description"],
            vectorizer_config={"vectorizer": "none"},
            properties=Config.WEAVIATE_SCHEMA["classes"][0]["properties"]
        )
    return client


@asynccontextmanager
async def createAsyncWeaviateClient():
    client = weaviate.use_async_with_local(
        host=Config.WEAVIATE_HOST,
        port=Config.WEAVIATE_PORT
    )
    await client.connect()
    try:
        schemaExists = await client.collections.exists(Config.DOCUMENT_CLASS_NAME)
        if not schemaExists:
            await client.collections.create(
                name=Config.WEAVIATE_SCHEMA["classes"][0]["class"],
                description=Config.WEAVIATE_SCHEMA["classes"][0]["description"],
                vectorizer_config={"vectorizer": "none"},
                properties=Config.WEAVIATE_SCHEMA["classes"][0]["properties"]
            )
        yield client
    finally:
        await client.close()


def generatePromptTemplate(templateStr: str, promptRole: str) -> list:
    return [
            ChatMessage(
                role=promptRole, 
                content=templateStr
            ),
        ]


def wrapPromptWithLanguageInstruction(language: str, prompt: str) -> str:
    lanuageInstruction = Config.LANGUAGE_INSTRUCTIONS.get(language, "")
    return f"{prompt}\n{lanuageInstruction}"


def getTopicList() -> list:
    topics = []
    for topic in Config.TOPICS:
        topics.append(topic["topic"])
    return topics


def getTopic(response: str) -> str:
    if response is None:
        return ""
    word = ""
    for i, letter in enumerate(list(response)[::-1]):
        if re.match("[A-Za-z]", letter):
            word = letter.lower() + word
        if not re.match("[A-Za-z]", letter) or len(response) == i+1:
            if word in getTopicList():
                return word
            word = ""
    return ""


def isTopicInTopics(topic: str=None) -> bool:
    if topic is None:
        return False
    return topic in getTopicList()


async def isVectorDbEmpty() -> bool:
    response = None
    async with createAsyncWeaviateClient() as client:
        collection = client.collections.get(Config.DOCUMENT_CLASS_NAME)
        response = (
            await collection.query.fetch_objects(
                return_properties=["file_name"]
            )
        )
    if response == None:
        return True
    else:
        return len(response.objects) == 0


async def isTopicInVectorDb(topic: str=None) -> bool:
    if topic is None:
        return False
    response = None
    async with createAsyncWeaviateClient() as client:
        collection = client.collections.get(Config.DOCUMENT_CLASS_NAME)
        response = (
            await collection.query.fetch_objects(
                return_properties=["file_name", Config.DOCUMENT_TOPIC_PROPERTY],
                filters=Filter.by_property(Config.DOCUMENT_TOPIC_PROPERTY).equal(topic),
                limit=1
            )
        )
    if response is None:
        return False
    else:
        return len(response.objects)>0


async def isRagUsedByTopic(topic: str=None) -> bool:
    if topic is None:
        return False
    for confTopic in Config.TOPICS:
        if topic == confTopic["topic"]:
            if confTopic["is_rag_used"]:
                return await isTopicInVectorDb(topic)
    return False


def generateTopicSelectingQuery(query: QueryResponseElement) -> QueryResponseElement:
    topics = []
    for topic in getTopicList():
        topics.append(topic)
    topicSelectingQuery = query.model_copy(
        update={
            "query":  ChatElement(
                chat_id=query.query.chat_id,
                chat_role=query.query.chat_role,
                chat_message=Config.TOPIC_SELECTING_QUESTION_TEMPLATE.format(
                    topics="\n- ".join(topics), 
                    chat_history=query.query.chat_message
                ),
                created_at=query.query.created_at,
                user_id=query.query.user_id
            ),
            "chat_history": []
        },
        deep=True
    )
    return topicSelectingQuery


def getTopicMetadataFilter(topic: str) -> MetadataFilters:
    return MetadataFilters(
        filters=[
            ExactMatchFilter(key=Config.DOCUMENT_TOPIC_PROPERTY, value=topic)
        ]
    )