import requests
import uuid
import random
import time
from datetime import datetime, timezone
from src.utils import setup_logger

logger = setup_logger()

PUBLISH_URL = "http://localhost:8000/publish"

TOPICS = ["sensor-temp", "sensor-humidity", "system-log", "user-activity"]
SOURCES = ["raspberry-pi", "iot-hub", "mobile-app"]

def generate_event(topic=None, source=None):
    return {
        "topic": topic or random.choice(TOPICS),
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": source or random.choice(SOURCES),
        "payload": {
            "value": random.randint(0, 100),
            "status": random.choice(["ok", "warn", "error"])
        }
    }

def simulate_delivery(batch_size=10, duplication_rate=0.2, delay=0.3):
    logger.info(f"Simulating {batch_size} events with {int(duplication_rate*100)}% duplicates...")
    events = [generate_event() for _ in range(batch_size)]

    # Randomly duplicate some events
    duplicates = random.sample(events, int(batch_size * duplication_rate))
    all_events = events + duplicates
    random.shuffle(all_events)

    for i, event in enumerate(all_events):
        response = requests.post(PUBLISH_URL, json=event)


        time.sleep(delay)

if __name__ == "__main__":
    simulate_delivery(batch_size=20, duplication_rate=0.25, delay=0.1)
