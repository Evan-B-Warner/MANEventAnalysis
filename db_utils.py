
def fetch_events(db_conn, match_id):
    events_query = (
    """
    SELECT
        event_id,
        type,
        subtype,
        result,
        start_time,
        end_time
    FROM
        events
    WHERE
        match_id = %s
    """)
    return db_conn.execute_and_read(events_query, (match_id,))


def fetch_event_participants(db_conn, match_id):
    participants_query = (
    """
    SELECT
        ep.event_id,
        ep.tracker_id,
        ep.type
    FROM
        event_participants ep LEFT JOIN
        events e ON ep.event_id = e.event_id 
    WHERE
        e.match_id = %s
    """)
    return db_conn.execute_and_read(participants_query, (match_id,))


def format_events_and_participants(events, participants):
    # format participants to index by event id
    formatted_participants = {}
    for participant in participants:
        event_id = participant["event_id"]
        if event_id not in formatted_participants:
            formatted_participants[event_id] = {}
        formatted_participants[event_id][participant["type"]] = participant["tracker_id"]

    # format events to index events and participants by event id
    formatted_events = {}
    for event in events:
        event_id = event["event_id"]
        formatted_events[event_id] = {
            "type": event["type"],
            "subtype": event["subtype"],
            "result": event["result"],
            "start_time": event["start_time"],
            "end_time": event["end_time"],
            "participants": formatted_participants[event_id],
        }
    return formatted_events


def fetch_and_format_player_bboxes(db_conn, match_id):
    # fetch bboxes
    query = (
    """
    SELECT
        tracker_id,
        pitch_x,
        pitch_y,
        timestamp
    FROM
        player_overlay_bboxes
    WHERE
        match_id = %s
    """)
    bboxes = db_conn.execute_and_read(query, (match_id,))

    # format by tracker_id
    formatted_bboxes = {}
    for bbox in bboxes:
        tracker_id = bbox["tracker_id"]
        if tracker_id not in formatted_bboxes:
            formatted_bboxes[tracker_id] = []
        formatted_bboxes[tracker_id].append({"timestamp": bbox["timestamp"], "x": bbox["pitch_x"], "y": bbox["pitch_y"]})
    return formatted_bboxes


def fetch_match_event_data(db_conn, match_id):
    # fetch events and participants
    events = fetch_events(db_conn, match_id)
    participants = fetch_event_participants(db_conn, match_id)

    # format events and participants to index by event id
    formatted_events = format_events_and_participants(events, participants)

    # fetch and format player bboxes
    formatted_bboxes = fetch_and_format_player_bboxes(db_conn, match_id)
    return formatted_events, formatted_bboxes