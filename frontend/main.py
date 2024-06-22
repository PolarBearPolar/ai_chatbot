from uvicorn import Config, Server
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from model import ChatElement, User
from database import getSession
from sqlalchemy import delete, and_, func
import time

app = FastAPI()
uvicornConfig = Config(
    app, 
    host="http://127.0.0.1",
    port="8000",
    log_level = "info",
    reload=True
)

# Create new user
@app.post("/user/", response_model=User)
def createUser(user: User, session: Session=Depends(getSession)):
    statement = select(User).where(and_(User.username == user.username, User.user_password == user.user_password))
    results = session.exec(statement).all()
    if len(results) > 0:
        raise HTTPException(status_code=404, detail="User has already been created.")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Get existing user by name and password
@app.get("/user/", response_model=User)
def getUser(username: str="", password: str="", session: Session=Depends(getSession)):
    statement = select(User).where(and_(User.username == username, User.user_password == password))
    results = session.exec(statement).all()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return results[0]

# Get existing user by id
@app.get("/user/{userId}", response_model=User)
def getUserById(userId: str, session: Session=Depends(getSession)):
    dbUser = session.get(User, userId)
    if not dbUser:
        raise HTTPException(status_code=404, detail="User not found.")
    return dbUser

# Change existing user information (age, gender)
@app.put("/user/{userId}", response_model=User)
def updateUser(userId: str, user: User, session: Session=Depends(getSession)):
    dbUser = session.get(User, userId)
    if not dbUser:
        raise HTTPException(status_code=404, detail="User not found.")
    dbUser.user_gender = user.user_gender if user.user_gender is not None else dbUser.user_gender
    dbUser.user_age = user.user_age if user.user_age is not None else dbUser.user_age
    session.add(dbUser)
    session.commit()
    session.refresh(dbUser)
    return dbUser

# Create new chat query and response to it
@app.post("/query/", response_model=list[ChatElement])
def createChatElements(chatElement: ChatElement, session: Session=Depends(getSession)):
    session.add(chatElement)
    session.commit()
    session.refresh(chatElement)
    time.sleep(5)
    responseChatElement = ChatElement(
        chat_id=chatElement.chat_id,
        chat_role="ASSISTANT",
        chat_message=f"echo: {chatElement.chat_message}",
        user_id=chatElement.user_id
    )
    session.add(responseChatElement)
    session.commit()
    session.refresh(responseChatElement)
    statement = select(ChatElement).where(and_(ChatElement.user_id == chatElement.user_id, ChatElement.chat_id == chatElement.chat_id))
    results = session.exec(statement).all()
    return results

# Get all chat elements of one chat for specific user (when userId and chatElementId are specified)
# Get distinct chats of user (when only userId is specified)
@app.get("/query/", response_model=list[ChatElement])
def getUserChatElements(userId: str=None, chatElementId: str=None, session: Session=Depends(getSession)):
    if not userId:
        return []
    if  chatElementId is not None:
        statement = select(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId))
        results = session.exec(statement).all()
        return results
    else:
        rowNumberFunction = func.row_number().over(partition_by=ChatElement.chat_id, order_by=ChatElement.created_at).label("row_num")
        subquery = (
            select(ChatElement.chat_id, ChatElement.created_at, rowNumberFunction)
            .subquery()
        )
        statement = select(ChatElement).join(subquery, and_(ChatElement.chat_id==subquery.c.chat_id, ChatElement.created_at==subquery.c.created_at)).where(and_(ChatElement.user_id == userId, subquery.c.row_num == 1))
        results = session.exec(statement).all()
        return results

# Delete chat for specific user
@app.delete("/query/")
def deleteChat(userId: str=None, chatElementId: str=None, session: Session=Depends(getSession)):
    if not userId or not chatElementId:
        return None
    statement = select(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId))
    results = session.exec(statement).all()
    if len(results) > 0:
        statement = delete(ChatElement).where(and_(ChatElement.user_id == userId, ChatElement.chat_id == chatElementId))
        session.exec(statement)
        session.commit()

if __name__ == "__main__":
    server = Server(uvicornConfig)
    server.run()