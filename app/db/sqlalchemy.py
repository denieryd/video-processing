from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


def init_db():
    engine = create_engine("sqlite:///frames.db", echo=True)
    session_fabric = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, session_fabric
