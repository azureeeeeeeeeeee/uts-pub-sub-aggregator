from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from src.utils import Base

class DedupEvent(Base):
    __tablename__ = "dedup"

    topic = Column(String, primary_key=True)
    event_id = Column(String, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    source = Column(String)
    payload = Column(JSON)