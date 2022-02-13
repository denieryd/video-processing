from sqlalchemy import Column, Integer, String

from app.db.sqlalchemy import Base, init_db


class VideoFrame(Base):
    __tablename__ = "video_frames"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    video_name: str = Column(String, nullable=False)
    frame_number: str = Column(Integer, nullable=False)
    timestamp: str = Column(String, nullable=False)
    rle: str = Column(String, nullable=False)


engine, session_fabric = init_db()
Base.metadata.create_all(engine)
