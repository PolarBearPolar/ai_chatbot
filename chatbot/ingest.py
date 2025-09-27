import os
import helper
import logging
import sys
import warnings
from weaviate import Client
from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from config import Config


warnings.filterwarnings("ignore")
# Set up logging
logging.basicConfig(
	level=Config.LOG_LEVEL,
	format=Config.LOG_FORMAT,
	handlers=[
		logging.FileHandler(Config.LOG_FILE, mode="a"),
        logging.StreamHandler()
	]
)
logger = logging.getLogger(__name__)


# Set global variables
topic = None


def main():
    # Get topic
    if len(sys.argv) < 2:
        logger.error(f"Please provide a topic argument that will indicate what topic the new documents will be releated to. The list of available topics - {', '.join(helper.getTopicList())}.")
        sys.exit(1)
    global topic
    topic = sys.argv[1]
    if not helper.isTopicInTopics(topic):
        logger.error(f"The topic '{topic}' is not supported. The list of available topics - {', '.join(helper.getTopicList())}.")
        sys.exit(1)
    # Try to ingest documents
    helper.configureSettings()
    client = helper.createWeaviateClient()
    documents = selectNewDocuments(client)
    ingestDocuments(client, documents, topic)
    logger.info("Done ingesting...")


def selectNewDocuments(weaviateClient: Client) -> SimpleDirectoryReader:
    collection = weaviateClient.collections.get(Config.DOCUMENT_CLASS_NAME)
    response = (
        collection.query.fetch_objects(
            return_properties=["file_name", Config.DOCUMENT_TOPIC_PROPERTY]
        )
    )
    storedDocs = response.objects
    loadedDocs = set()
    for doc in storedDocs:
        loadedDocs.add(os.path.basename(doc.properties.get("file_name", None)))
    if len(loadedDocs) > 0:
        logger.info(f"The following documents have already been ingested before:\t{loadedDocs}")
    docsToUpload = []
    for element in os.listdir(Config.DOCUMENTS_DIRECTORY):
        if element in loadedDocs:
            continue
        fullElementPath = os.path.join(Config.DOCUMENTS_DIRECTORY, element)
        docsToUpload.append(fullElementPath)
        logger.info(f"{fullElementPath} will be uploaded to the vector DB ...")
    if len(docsToUpload) > 0:
        newDocuments = SimpleDirectoryReader(input_files = docsToUpload, file_metadata=getFileMetadata).load_data()
    else:
        newDocuments = None
    return newDocuments


def ingestDocuments(weaviateClient: Client, documents: SimpleDirectoryReader, topic: str) -> None:
    if documents is not None:
        vectorStore = WeaviateVectorStore(
            weaviate_client = weaviateClient, 
            index_name = Config.DOCUMENT_CLASS_NAME, 
            text_key = Config.DOCUMENT_CONTENT_PROPERTY
        )
        storageContext = StorageContext.from_defaults(vector_store = vectorStore)
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context = storageContext
        )
        logger.info("The documents have been ingested into the vector DB...")


def getFileMetadata(filename: str):
    global topic
    return {Config.DOCUMENT_TOPIC_PROPERTY: topic, "file_name": filename}


if __name__ == "__main__":
    main()