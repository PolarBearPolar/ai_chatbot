import constants
# from sqlmodel import create_engine, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# engine = create_engine(constants.DATABASE_URL, echo=True)
engine = create_async_engine(constants.DATABASE_URL, echo=True, future=True)

# Session factory
asyncSessionMaker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def getSession() -> AsyncSession:
#    with Session(engine) as session:
#        yield session
    async with asyncSessionMaker() as session:
        yield session
