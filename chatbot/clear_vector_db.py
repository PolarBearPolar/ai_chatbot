import helper
from config import Config

logger = helper.getFileLogger(__name__)

def main():
    try:
        client = helper.createWeaviateClient()
        client.batch.delete_objects(
            class_name=Config.DOCUMENT_CLASS_NAME,
            where={
                "path": [Config.DOCUMENT_CONTENT_PROPERTY],
                "operator": "Like",
                "valueText": "*"
            }
        )
        client.schema.delete_class(Config.DOCUMENT_CLASS_NAME)
        logger.info("The vector database has been cleared...")
    except:
        pass

if __name__=="__main__":
    main()