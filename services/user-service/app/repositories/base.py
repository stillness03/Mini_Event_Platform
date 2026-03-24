from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def commit(self):
        self.db.commit()

    def refresh(self, instance):
        self.db.refresh(instance)
        return instance
    
    def flush(self):
        self.db.flush()

    def rollback(self):
        self.db.rollback()