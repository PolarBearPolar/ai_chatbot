import constants
from sqlmodel import create_engine, Session

engine = create_engine(constants.DATABASE_URL, echo=True)

def getSession():
    with Session(engine) as session:
        yield session
