import helper
import logging
from llama_index.core import VectorStoreIndex, Settings, ChatPromptTemplate
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.base.base_query_engine import BaseQueryEngine
from typing import List
from config import Config
from model import ChatElement, QueryResponseElement
from datetime import datetime, timezone


logger = logging.getLogger(__name__)


def retrieveResponse(query: QueryResponseElement, language: str) -> None:
    # Get topic that question is related to first
    logger.info(f"Trying to answer the query:\n\tRAG is enabled: {query.is_rag_used}\n\tlanguage: {language}\n\tquery:\n{query.query.chat_message}")
    topicSelectingQuery = helper.generateTopicSelectingQuery(query)
    retrieveResponseWithoutRag(topicSelectingQuery, language)
    topic = topicSelectingQuery.response.chat_message.lower()
    logger.info(f"The topic of the query defined by the LLM: '{topic}'.")
    # Based on RAG usage and/or topic, route query to function
    if not query.is_rag_used:
        logger.info(f"RAG is not enabled in the backend service of the application.")
        retrieveResponseWithoutRag(query, language, Config.SYSTEM_ROLE)
    elif helper.isRagUsedByTopic(topic):
        logger.info(f"The topic uses RAG.")
        retrieveResponseWithRag(query, language, topic, Config.SYSTEM_ROLE)
    else:
        logger.info(f"The topic does not use RAG.")
        retrieveResponseWithoutRag(query, language, Config.SYSTEM_ROLE) 


def retrieveResponseWithRag(query: QueryResponseElement, language: str, topic: str, systemRolePrompt: str=None)-> None:
    helper.configureSettings()
    index = getIndex()
    chatHistory = []
    if systemRolePrompt is not None:
        chatHistory.append(
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    helper.wrapPromptWithLanguageInstruction(language, systemRolePrompt)
                )
            )
        )
    if len(query.chat_history) > 0:
        chatHistory.extend(query.getTransformedChatHistory())
    logger.debug(f"Here comes chat history: {chatHistory}")
    for el in chatHistory:
        logger.debug(f" - {str(el)}")
    queryEngine = getQueryEngine(index, chatHistory, language, topic)
    response = queryEngine.query(query.query.chat_message).response
    query.response = ChatElement(
        chat_id = query.query.chat_id,
        chat_role = Config.ROLE_ASSISTANT,
        chat_message = response,
        created_at = datetime.now(timezone.utc),
        user_id = query.query.user_id
    )


def retrieveResponseWithoutRag(query: QueryResponseElement, language: str, systemRolePrompt: str=None) -> None:
    llm = helper.getLlm()
    chatHistory = []
    if systemRolePrompt is not None:
        chatHistory.append(
            ChatMessage(
                role=MessageRole.SYSTEM,
                content=(
                    helper.wrapPromptWithLanguageInstruction(language, systemRolePrompt)
                )
            )
        )
    if len(query.chat_history) > 0:
        chatHistory.extend(query.getTransformedChatHistory())
    chatHistory.append(
        ChatMessage(
            role=MessageRole.USER,
            content=query.query.chat_message
        )
    )
    logger.debug(f"Here comes chat history: {chatHistory}")
    for el in chatHistory:
        logger.debug(f" - {str(el)}")
    response = llm.chat(chatHistory).message.content
    query.response = ChatElement(
        chat_id = query.query.chat_id,
        chat_role = Config.ROLE_ASSISTANT,
        chat_message = response,
        created_at = datetime.now(timezone.utc),
        user_id = query.query.user_id
    )


def getIndex() -> VectorStoreIndex:
    client = helper.createWeaviateClient()
    vectorStore = WeaviateVectorStore(
        weaviate_client=client, 
        index_name=Config.DOCUMENT_CLASS_NAME, 
        text_key=Config.DOCUMENT_CONTENT_PROPERTY
    )
    index = VectorStoreIndex.from_vector_store(
        vectorStore, 
        embed_model=helper.getEmbeddingModdel()
    )
    return index


def getQueryEngine(index: VectorStoreIndex, chatHistoryMessages: List[ChatMessage], language: str, topic: str) -> BaseQueryEngine:
    queryEngine = index.as_query_engine(
        llm=helper.getLlm(),
        filters=helper.getTopicMetadataFilter(topic),
        similarity_top_k=Config.SIMILARITY_TOP_KEY,
        text_qa_template=ChatPromptTemplate(
            chatHistoryMessages + helper.generatePromptTemplate(helper.wrapPromptWithLanguageInstruction(language, Config.TEXT_QA_TEMPLATE_STR), MessageRole.USER)
        ),
        refine_template=ChatPromptTemplate(
            chatHistoryMessages + helper.generatePromptTemplate(helper.wrapPromptWithLanguageInstruction(language, Config.REFINE_TEMPLATE_STR), MessageRole.USER)
        )
    )
    return queryEngine


def getChatElementResponse(chatElementQuery: ChatElement, response: str, timeTaken: float, chatId: str) -> ChatElement:
    chatElementResponse = ChatElement(
        isRagUsed=chatElementQuery.isRagUsed,
        chatId=chatId,
        query=chatElementQuery.query,
        answer=response,
        timeTaken=timeTaken
    )
    return chatElementResponse
