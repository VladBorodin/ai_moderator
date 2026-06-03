from app import models
from app.db.cleanup_db import cleanup_db
from app.db.seed_db import seed_db
from app.db.session import Base, SessionLocal, engine


def init_db() -> None:
	Base.metadata.create_all(bind=engine)

	db = SessionLocal()

	try:
		seed_db(db)
		cleanup_db(db)
	finally:
		db.close()