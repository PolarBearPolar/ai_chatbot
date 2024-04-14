import os
import helper
from weaviate import Client
from llama_index.core import VectorStoreIndex, StorageContext, SimpleDirectoryReader, Settings
from llama_index.vector_stores.weaviate import WeaviateVectorStore
from config import Config

logger = helper.getFileLogger(__name__)

def main():
    helper.configureSettings()
    client = helper.createWeaviateClient()
    documents = selectNewDocuments(client)
    ingestDocuments(client, documents)
    logger.info("Done ingesting...")


def selectNewDocuments(weaviateClient: Client) -> SimpleDirectoryReader:
    response = (
        weaviateClient.query
        .get(Config.DOCUMENT_CLASS_NAME, ["file_name"])
        .do()
    )
    storedDocs = response.get("data", {}).get("Get", {}).get(Config.DOCUMENT_CLASS_NAME, [])
    loadedDocs = set()
    for doc in storedDocs:
        loadedDocs.add(os.path.basename(doc.get("file_name", None)))
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
        newDocuments = SimpleDirectoryReader(input_files = docsToUpload).load_data()
    else:
        newDocuments = None
    return newDocuments


def ingestDocuments(weaviateClient: Client, documents: SimpleDirectoryReader) -> None:
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
    

if __name__ == "__main__":
    main()