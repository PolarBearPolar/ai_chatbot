import helper
import time
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.chat_engine import CondenseQuestionChatEngine
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.base.base_query_engine import BaseQueryEngine
from typing import List
from config import Config
from model import ChatElement, QueryResponseElement
from datetime import datetime, timezone


logger = helper.getFileLogger(__name__)

def retrieveResponse(query: QueryResponseElement) -> None:
    logger.debug(f"Trying to answer the query:\n\tRAG is enabled: {query.is_rag_used}\n\tquery:\n{query.query.chat_message}")
    if query.is_rag_used:
        retrieveResponseWithRag(query)
    elif not query.is_rag_used:
        retrieveResponseWithoutRag(query)


def retrieveResponseWithRag(query: QueryResponseElement)-> None:
    helper.configureSettings()
    index = getIndex()
    if len(query.chat_history) > 0:
        logger.debug("Using chat engine...")
        chatEngine = getChatEngine(index, query.getTransformedChatHistory())
        response = chatEngine.chat(query.query.chat_message).response
    else:
        logger.debug("Using query engine...")
        queryEngine = getQueryEngine(index)
        response = queryEngine.query(query.query.chat_message).response
    query.response = ChatElement(
        chat_id = query.query.chat_id,
        chat_role = Config.ROLE_ASSISTANT,
        chat_message = response,
        created_at = datetime.now(timezone.utc),
        user_id = query.query.user_id
    )


def retrieveResponseWithoutRag(query: QueryResponseElement) -> None:
    llm = helper.getLlm()
    if len(query.chat_history) > 0:
        logger.debug("Using chat engine...")
        transformedChatHistory = query.getTransformedChatHistory()
        transformedChatHistory.append(
            ChatMessage(
                role=MessageRole.USER,
                content=query.query.chat_message
            )
        )
        response = llm.chat(transformedChatHistory).message.content
    else:
        logger.debug("Using query engine...")
        response = llm.complete(query.query.chat_message).text
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