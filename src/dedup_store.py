from sqlalchemy.exc import IntegrityError
from src.utils import SessionLocal
from src.models.dedup_model import DedupEvent

class DedupStoreORM:
    def __init__(self):
        self.db = SessionLocal()

    def is_duplicate(self, topic: str, event_id: str) -> bool:
        return (
            self.db.query(DedupEvent)
            .filter_by(topic=topic, event_id=event_id)
            .first()
            is not None
        )

    def mark_processed(self, topic: str, event_id: str):
        try:
            entry = DedupEvent(topic=topic, event_id=event_id)
            self.db.add(entry)
            self.db.commit()
        except IntegrityError:
            self.db.rollback()

    def close(self):
        self.db.close()