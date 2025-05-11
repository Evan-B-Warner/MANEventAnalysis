import os

from DBConnector import DBConnector
from common_utils import closest_coords
from db_utils import fetch_match_event_data, write_tags_to_db
from pass_utils import classify_pass
            

def analyze_events(events, bboxes):
    analyzed = []
    for event_id in events:
        event = events[event_id]
        event_type = event["type"]
        if event_type == "pass":
            passer_coords = closest_coords(event["start_time"]+1, bboxes[event["participants"]["passer"]])
            receiver_coords = closest_coords(event["end_time"]-1, bboxes[event["participants"]["receiver"]])
            tags = classify_pass(event, event_id, passer_coords["team"], receiver_coords["team"], passer_coords["x"], passer_coords["y"], receiver_coords["x"], receiver_coords["y"])
            analyzed.append({"event_id": event_id, "tags": tags})

    return analyzed


if __name__ == "__main__":
    # db connection
    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = "analytics_and_library"
    db_conn = DBConnector(host, user, password, database)

    # fetch data
    events, bboxes = fetch_match_event_data(db_conn, 4)

    # analyze and write events
    analyzed = analyze_events(events, bboxes)
    write_tags_to_db(db_conn, analyzed)