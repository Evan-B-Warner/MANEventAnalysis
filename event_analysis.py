import os

from DBConnector import DBConnector
from db_utils import fetch_match_event_data
from pass_utils import classify_pass

# default dimensions for the pitch
PITCH_HEIGHT = 105
PITCH_WIDTH = 68
# Note: pitch_x is the field length, pitch_y is the field width


def closest_coords(timestamp, coords):
    # finds the player coordinates at the closest time to the timestamp
    prev = None
    for i in range(len(coords)):
        coord = coords[i]
        current = coord["timestamp"]
        if current > timestamp:
            if prev is None or abs(current - timestamp) <= abs(prev - timestamp):
                return coord
            else:
                return coords[i-1]
    return coords[-1]
            

def analyze_events(events, bboxes):
    analyzed = []
    for event_id in events:
        event = events[event_id]
        event_type = event["type"]
        if event_type == "pass":
            passer_coords = closest_coords(event["start_time"]+1, bboxes[event["participants"]["passer"]])
            receiver_coords = closest_coords(event["end_time"]-1, bboxes[event["participants"]["receiver"]])
            tags = classify_pass(event, passer_coords["x"], passer_coords["y"], receiver_coords["x"], receiver_coords["y"])
            analyzed.append([event_id, tags])

    import json
    with open("analyzed_events.json", "w") as f:
        json.dump({"events": analyzed}, f, indent=4)


if __name__ == "__main__":
    # db connection
    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = "analytics_and_library"
    db_conn = DBConnector(host, user, password, database)

    # fetch data
    events, bboxes = fetch_match_event_data(db_conn, 4)

    # analyze events
    analyze_events(events, bboxes)