import weaviate
from llama_index.llms.together import TogetherLLM
from llama_index.core import Settings
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.core.llms import ChatMessage
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from llama_index.core.vector_stores import ExactMatchFilter, MetadataFilters
from config import Config
from model import ChatElement, QueryResponseElement


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


def isTopicInTopics(topic: str=None) -> bool:
    if topic is None:
        return False
    return topic in getTopicList()


def isVectorDbEmpty() -> bool:
    client = createWeaviateClient()
    response = (
        client.query
        .get(Config.DOCUMENT_CLASS_NAME, ["file_name"])
        .do()
    )
    storedDocs = response.get("data", {}).get("Get", {}).get(Config.DOCUMENT_CLASS_NAME, [])
    return len(storedDocs) == 0


def isTopicInVectorDb(topic: str=None) -> bool:
    if topic is None:
        return False
    configureSettings()
    client = createWeaviateClient()
    response = (
        client.query
        .get(Config.DOCUMENT_CLASS_NAME, ["file_name", Config.DOCUMENT_TOPIC_PROPERTY])
        .with_where({
            "path": [Config.DOCUMENT_TOPIC_PROPERTY],
            "operator": "Equal",
            "valueText": topic
        })
        .with_limit(1)
        .do()
    )
    entries = response.get("data", {}).get("Get", {}).get(Config.DOCUMENT_CLASS_NAME, [])
    return len(entries)>0


def isRagUsedByTopic(topic: str=None) -> bool:
    if topic is None:
        return False
    for confTopic in Config.TOPICS:
        if topic == confTopic["topic"]:
            if confTopic["is_rag_used"]:
                return isTopicInVectorDb(topic)
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

