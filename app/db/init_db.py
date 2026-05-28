from app.db.session import Base, engine

from app import models


def init_db() -> None:
	Base.metadata.create_all(bind=engine)