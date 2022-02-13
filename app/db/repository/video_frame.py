"""VideoFrame repository to work with db."""


from app.db.models import VideoFrame, session_fabric


class VideoFrameRepository:
    db_model = VideoFrame

    @classmethod
    def insert(cls, **kwargs):
        with session_fabric() as session, session.begin():
            session.add(cls.db_model(**kwargs))
