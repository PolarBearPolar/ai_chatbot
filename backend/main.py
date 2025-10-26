import constants
# import requests
import logging
import aiohttp
from uvicorn import Config, Server
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.encoders import jsonable_encoder
from sqlmodel import Session, select
from sqlalchemy.ext.asyncio import AsyncSession
from model import ChatElement, User, QueryResponseElement
from database import getSession
from sqlalchemy import delete, and_, func
from typing import Optional
from helper import getLanguage, sendRequestAsync

# Set up logging
logging.basicConfig(
	level=constants.LOG_LEVEL,
	format=constants.LOG_FORMAT,
	handlers=[
		logging.FileHandler(constants.LOG_FILE, mode="a")
	]
)
logger = logging.getLogger(__name__)

app = FastAPI()
uvicornConfig = Config(
    app, 
    host=constants.API_HOST,
    port=constants.API_PORT,
    log_level = "info",
    reload=True
)
session: aiohttp.ClientSession | None = None
    
@app.on_event("startup")
async def startupEvent():
    global session
    session = aiohttp.ClientSession(timeout = constants.CLIENT_TIMEOUT_CONFIG)

@app.on_event("shutdown")
async def shutdownEvent():
    await session.close()

# Create new user
@app.post("/user/", response_model=User)
async def createUser(user: User, db: AsyncSession=Depends(getSession)):
    statement = select(User).where(and_(User.username == user.username, User.user_password == user.user_password))
    results = await db.execute(statement)
    results = results.scalars().all()
    if len(results) > 0:
        raise HTTPException(status_code=404, detail="User has already been created.")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

# Get existing user by name and password
@app.get("/user/", response_model=User)
async def getUser(username: str="", password: str="", db: AsyncSession=Depends(getSession)):
    statement = select(User).where(and_(User.username == username, User.user_password == password))
    results = await db.execute(statement)
    user = results.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    return user

# Get existing user by id
@app.get("/user/{userId}", response_model=User)
async def getUserById(userId: str, db: AsyncSession=Depends(getSession)):
    dbUser = await db.get(User, userId)
    if not dbUser:
        raise HTTPException(status_code=404, detail="User not found.")
    return dbUser

# Change existing user information (age, gender)
@app.put("/user/{userId}", response_model=User)
async def updateUser(userId: str, user: User, db: AsyncSession=Depends(getSession)):
    dbUser = await db.get(User, userId)
    if not dbUser:
        raise HTTPException(status_code=404, detail="User not found.")
    dbUser.user_gender = user.user_gender if user.user_gender is not None else dbUser.user_gender
    dbUser.user_age = user.user_age if user.user_age is not None else dbUser.user_age
    db.add(dbUser)
    await db.commit()
    await db.refresh(dbUser)
    return dbUser

# Create new chat query and response to it
@app.post("/query/", response_model=Optional[ChatElement])
async def createChatElements(chatElement: ChatElement, db: AsyncSession=Depends(getSession), accept_language: str=Header(None)):
    logger.debug(f"Query object: {chatElement}")
    # Get chat history
    chatHistoryStatement = select(ChatElement).where(and_(ChatElement.user_id == chatElement.user_id, ChatElement.chat_id == chatElement.chat_id))
    results = await db.execute(chatHistoryStatement)
    chatHistory = results.scalars().all()
    # Save query chat element to database
    db.add(chatElement)
    await db.commit()
    await db.refresh(chatElement)
    # Build query object
    query = QueryResponseElement(
        is_rag_used=constants.IS_RAG_USED,
        query=chatElement,
        chat_history=jsonable_encoder(chatHistory)
    )
    logger.debug(f" ***** Request object ***** : {query.json()}")
    # Get response language
    language = getLanguage(accept_language)
    logger.info(f"A new query has been subitted: {query.query.chat_message}")
    # Send query object to chatbot component to get response
    status, response, error = await sendRequestAsync(
        session=session, 
        method="post", 
        url=f"{constants.CHATBOT_URL}/query", 
        headers={constants.API_HEADER_LANGUAGE: language},
        body=jsonable_encoder(query.model_dump())
    )
    logger.info(f"Chatbot response status: {status}, response error (if any): {error}")
    # Save response to database
    if status == 200 and response is not None and response.get("response", None) is not None and response.get("response").get("chat_message", None) is not None:
        responseChatElement = ChatElement(**response["response"])
        logger.debug(f" ***** Response object ***** : {response}")
        logger.info(f"The response to the query is as follows: {responseChatElement.chat_message}")
        db.add(responseChatElement)
        await db.commit()
        await db.refresh(responseChatElement)
        return responseChatElement
    return None

# Get all chat elements of one chat for specific user (when userId and chatElementId are specified)
# Get distinct chats of user (when only userId is specified)
@app.get("/query/", response_model=list[ChatElement])
async def getUserChatElements(userId: str=None, chatElementId: str=None, db: AsyncSession=Depends(getSession)):
    if not userId:
        return []
    if  chatElementId is not None:
        statement = select(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId)).order_by(ChatElement.created_at)
        results = await db.execute(statement)
        results = results.scalars().all()
        return results
    else:
        rowNumberFunction = func.row_number().over(partition_by=ChatElement.chat_id, order_by=ChatElement.created_at).label("row_num")
        subquery = (
            select(ChatElement.chat_id, ChatElement.created_at, rowNumberFunction)
            .subquery()
        )
        statement = select(ChatElement).join(subquery, and_(ChatElement.chat_id==subquery.c.chat_id, ChatElement.created_at==subquery.c.created_at)).where(and_(ChatElement.user_id == userId, subquery.c.row_num == 1))
        results = await db.execute(statement)
        results = results.scalars().all()
        return results

# Delete chat for specific user
@app.delete("/query/")
async def deleteChat(userId: str=None, chatElementId: str=None, db: AsyncSession=Depends(getSession)):
    if not userId or not chatElementId:
        return None
    statement = select(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId))
    results = await db.execute(statement)
    results = results.scalars().all()
    if len(results) > 0:
        statement = delete(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId))
        await db.execute(statement)
        await db.commit()

if __name__ == "__main__":
    server = Server(uvicornConfig)
    server.run()
