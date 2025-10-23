from fastapi import FastAPI, HTTPException, Depends, Request
from typing import List, Dict, Union
from src.utils import Base, engine, db, setup_logger, get_db
from src.models.dedup_model import DedupEvent
from src.models.schemas.dedup_schema import EventSchema
from datetime import datetime, timedelta, timezone
from sqlalchemy import distinct
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI()

START_TIME = datetime.now(timezone.utc)
STATS = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0,
}

logger = setup_logger()

@app.get("/")
def main():
    return {
        "message": "Hello world fastapi"
    }

@app.post("/publish")
async def publish_event(
    request: Request,
    db: Session = Depends(get_db)
):
    
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if isinstance(data, dict):
        events_data = [data]
    elif isinstance(data, list):
        events_data = data
    else:
        raise HTTPException(status_code=400, detail="Request body must be a JSON object or array")

    # logger.info(f"Received {len(events_data)} event(s).")
    logger.info(f"Server receive new data to be published")
    STATS["received"] += len(events_data)

    processed_ids = []
    duplicates = 0

    for raw_event in events_data:
        try:
            event = EventSchema(**raw_event)
        except Exception as e:
            logger.error(f"Invalid event data: {e}")
            raise HTTPException(status_code=400, detail=f"Invalid event format: {e}")

        logger.info(f"Processing event_id={event.event_id} from topic={event.topic}")

        existing = db.query(DedupEvent).filter_by(
            topic=event.topic,
            event_id=event.event_id
        ).first()

        if existing:
            logger.warning(f"Duplicate detected: event_id={event.event_id}")
            STATS["duplicate_dropped"] += 1
            duplicates += 1
            continue

        new_event = DedupEvent(
            event_id=event.event_id,
            topic=event.topic,
            source=event.source,
            timestamp=event.timestamp,
            payload=event.payload
        )
        db.add(new_event)
        processed_ids.append(event.event_id)

    db.commit()

    STATS["unique_processed"] += len(processed_ids)
    logger.info(f"Processed {len(processed_ids)} new event(s), {duplicates} duplicate(s) dropped.")

    return {
        "status": "ok",
        "processed": processed_ids,
        "duplicates": duplicates,
        "total_received": len(events_data)
    }


@app.get("/events")
def get_events(topic):
    logger.info("Server received a request to get all events data")
    logger.info("Querying the desired data. . .")
    query = db.query(DedupEvent)
    if topic:
        query = query.filter_by(topic=topic)

    events = query.all()

    if not events:
        logger.warning(f"No events with topic {topic} is being found !!!")
        raise HTTPException(status_code=404, detail="No events found")

    logger.info("Query is done. . .")
    logger.info("Returning the data into the client. . .")

    return [
        {
            "event_id": e.event_id,
            "topic": e.topic,
            "source": e.source,
            "timestamp": e.timestamp.isoformat(),
            "payload": e.payload
        }
        for e in events
    ]


@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    logger.info("Server receive a request to get server status")
    topics = [row[0] for row in db.query(distinct(DedupEvent.topic)).all()]
    uptime = datetime.now(timezone.utc) - START_TIME
    logger.info("Returning all status data into client")

    return {
        "received": STATS["received"],
        "unique_processed": STATS["unique_processed"],
        "duplicate_dropped": STATS["duplicate_dropped"],
        "topics": topics,
        "uptime": str(timedelta(seconds=int(uptime.total_seconds())))
    }