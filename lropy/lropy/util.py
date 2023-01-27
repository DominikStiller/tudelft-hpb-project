import os
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


def get_average_load(normalize=True):
    with open("/proc/loadavg") as f:
        # Averages over last 1, 5 and 10 min periods
        load_averages = [float(avg) for avg in f.readline().split(" ")[:3]]

    if normalize:
        n_cpus = os.cpu_count()
        load_averages = [avg / n_cpus for avg in load_averages]

    # Return 10-min average load
    return load_averages[2]


if __name__ == '__main__':
    print(get_average_load())
