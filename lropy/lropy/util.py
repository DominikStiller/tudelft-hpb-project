import uuid
from datetime import datetime


def generate_id(length: int = 5):
    return str(uuid.uuid4().hex)[:length]


def generate_folder_name(timestamp: datetime = None, id: str = None) -> str:
    if timestamp is None:
        timestamp = datetime.now()
    timestamp_string = timestamp.replace(microsecond=0).isoformat()

    if id is None:
        id = generate_id()

    return timestamp_string.replace(":", "-") + "-" + id
