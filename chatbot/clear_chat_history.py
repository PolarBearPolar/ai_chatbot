import helper

logger = helper.getFileLogger(__name__)

def main():
    chatHistory = helper.getChatHistory()
    chatHistory.clearHistory()
    logger.info("Chat history has been deleted...")

if __name__=="__main__":
    main()