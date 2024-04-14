import helper
import time
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.base.base_query_engine import BaseQueryEngine
from typing import List
from chat_history import ChatHistory
from config import Config
from chat_element import ChatElement


logger = helper.getFileLogger(__name__)

def retrieveResponse(chatElementQuery: ChatElement) -> ChatElement:
    response = None
    logger.debug(f"Trying to answer the query:\n\tRAG is enabled: {chatElementQuery.isRagUsed}\n\tchat id: {chatElementQuery.chatId}\n\tquery:\n{chatElementQuery.query}")
    if chatElementQuery.isRagUsed:
        response = retrieveResponseWithRag(chatElementQuery)
    elif not chatElementQuery.isRagUsed:
        response = retrieveResponseWithoutRag(chatElementQuery)
    return response


def retrieveResponseWithRag(chatElementQuery: ChatElement) -> ChatElement:
    startTime = time.time()
    helper.configureSettings()
    index = getIndex()
    chatHistory = helper.getChatHistory()
    chatHistoryId, chatHistoryMessages = chatHistory.getMessages(chatId=chatElementQuery.chatId)
    if len(chatHistoryMessages) > 0:
        logger.debug("Using chat engine...")
        chatEngine = getChatEngine(index, chatHistoryMessages)
        response = chatEngine.chat(chatElementQuery.query).response
    else:
        logger.debug("Using query engine...")
        queryEngine = getQueryEngine(index)
        response = queryEngine.query(chatElementQuery.query).response
    chatHistory.insertMessages(chatHistoryId, ChatHistory.ROLE_HUMAN, chatElementQuery.query)
    chatHistory.insertMessages(chatHistoryId, ChatHistory.ROLE_ASSISTANT, response)
    endTime = time.time()
    timeTaken = round(endTime - startTime, Config.TIME_TAKEN_DIGIT_NUMBER)
    logger.debug(f"A response has been generated in {timeTaken} sec...")
    chatElementResponse = getChatElementResponse(chatElementQuery, response, timeTaken, chatHistoryId)
    return chatElementResponse


def retrieveResponseWithoutRag(chatElementQuery: ChatElement) -> ChatElement:
    startTime = time.time()
    llm = helper.getLlm()
    chatHistory = helper.getChatHistory()
    chatHistoryId, chatHistoryMessages = chatHistory.getMessages(chatId=chatElementQuery.chatId)
    if len(chatHistoryMessages) > 0:
        logger.debug("Using chat engine...")
        chatHistoryMessages.append(
            ChatMessage(
                role=MessageRole.USER,
                content=chatElementQuery.query
            )
        )
        response = llm.chat(chatHistoryMessages).message.content
    else:
        logger.debug("Using query engine...")
        response = llm.complete(chatElementQuery.query).text
    chatHistory.insertMessages(chatHistoryId, ChatHistory.ROLE_HUMAN, chatElementQuery.query)
    chatHistory.insertMessages(chatHistoryId, ChatHistory.ROLE_ASSISTANT, response)
    endTime = time.time()
    timeTaken = round(endTime - startTime, Config.TIME_TAKEN_DIGIT_NUMBER)
    logger.debug(f"A response has been generated in {timeTaken} sec...")
    chatElementResponse = getChatElementResponse(chatElementQuery, response, timeTaken, chatHistoryId)
    return chatElementResponse


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


def getQueryEngine(index: VectorStoreIndex) -> BaseQueryEngine:
    queryEngine = index.as_query_engine(
        llm=helper.getLlm(),
        similarity_top_k=Config.SIMILARITY_TOP_KEY,
        text_qa_template=Config.TEXT_QA_TEMPLATE,
        refine_template=Config.REFINE_TEMPLATE
    )
    return queryEngine


def getChatEngine(index: VectorStoreIndex, chatHistoryMessages: List[ChatMessage]) -> CondenseQuestionChatEngine:
    chatEngine = CondenseQuestionChatEngine.from_defaults(
        query_engine=getQueryEngine(index),
        llm=helper.getLlm(),
        chat_history=chatHistoryMessages,
        verbose=True
    )
    return chatEngine


def getChatElementResponse(chatElementQuery: ChatElement, response: str, timeTaken: float, chatId: str) -> ChatElement:
    chatElementResponse = ChatElement(
        isRagUsed=chatElementQuery.isRagUsed,
        chatId=chatId,
        query=chatElementQuery.query,
        answer=response,
        timeTaken=timeTaken
    )
    return chatElementResponse