from sqlmodel import create_engine, Session

DATABASE_URL = "postgresql://admin:admin@localhost:5440/chatbot"

engine = create_engine(DATABASE_URL, echo=True)

def getSession():
    with Session(engine) as session:
        yield session