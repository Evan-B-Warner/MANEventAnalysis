import os
from tqdm import tqdm

from DBConnector import DBConnector
from common_utils import closest_coords
from db_utils import fetch_match_event_data, write_tags_to_db
from pass_utils import classify_pass
from assist_utils import classify_assists
from shot_utils import classify_shot
from duel_utils import classify_duel
from carry_utils import classify_carry
from losses_and_recovery_utils import classify_losses_and_interceptions, classify_recoveries
from infraction_utils import classify_infraction


def analyze_events(events, bboxes):
    print("Analyzing Events...")
    analyzed = {}
    for event_id in tqdm(events):
        event = events[event_id]
        event_type = event["type"]
        tags = []

        # passes
        if event_type == "pass":
            passer_id, receiver_id = event["participants"]["passer"], event["participants"]["receiver"]
            if passer_id not in bboxes or receiver_id not in bboxes:
                continue
            passer_coords = closest_coords(event["start_time"]+1, bboxes[passer_id])
            receiver_coords = closest_coords(event["end_time"]-1, bboxes[receiver_id])
            tags = classify_pass(event, passer_coords["team"], receiver_coords["team"], passer_coords["x"], passer_coords["y"], receiver_coords["x"], receiver_coords["y"], bboxes)
       
        # shots
        elif event_type == "shot":
            tags = classify_shot(event)
        
        # duels
        elif event_type == "duel":
            tags = classify_duel(event)
        
        # carries
        elif event_type == "carry":
            carrier_id = event["participants"]["carrier"]
            if carrier_id not in bboxes:
                continue
            start_coords = closest_coords(event["start_time"]+1, bboxes[carrier_id])
            end_coords = closest_coords(event["end_time"]-1, bboxes[carrier_id])
            tags = classify_carry(event, start_coords["team"], start_coords["x"], start_coords["y"], end_coords["x"], end_coords["y"])

        # infractions
        elif event_type == "infraction":
            tags = classify_infraction(event)

        # losses and interceptions
        tags.extend(classify_losses_and_interceptions(event, bboxes))

        # save the tags
        analyzed[event_id] = tags[:]
    
    print("Classifying Assists and Recoveries...")
    # assists
    assists = classify_assists(events, bboxes)
    for assist_type in assists:
        for assist in assists[assist_type]:
            event_id = assist["event_id"]
            if event_id not in analyzed:
                analyzed[event_id] = []
            analyzed[assist["event_id"]].append(assist_type)
    
    # recoveries
    recoveries = classify_recoveries(events, bboxes)
    for event_id in recoveries:
        if event_id not in analyzed:
            analyzed[event_id] = []
        analyzed[event_id].append(recoveries[event_id])

    return analyzed


if __name__ == "__main__":
    # db connection
    host = os.environ["DB_HOST"]
    user = os.environ["DB_USER"]
    password = os.environ["DB_PASSWORD"]
    database = "analytics_and_library"
    db_conn = DBConnector(host, user, password, database)

    # fetch data
    events, bboxes = fetch_match_event_data(db_conn, 6)

    # analyze and write events
    analyzed = analyze_events(events, bboxes)
    write_tags_to_db(db_conn, analyzed)