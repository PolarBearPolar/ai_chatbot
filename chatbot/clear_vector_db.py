import helper
import logging
from config import Config

# Set up logging
logging.basicConfig(
	level=Config.LOG_LEVEL,
	format=Config.LOG_FORMAT,
	handlers=[
		logging.FileHandler(Config.LOG_FILE, mode="a")
	]
)
logger = logging.getLogger(__name__)

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