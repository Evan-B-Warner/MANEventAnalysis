

# default dimensions for the pitch
PITCH_LENGTH = 105
PITCH_WIDTH = 68
# Note: pitch_x is the field length, pitch_y is the field width

def check_team(event, tracker_id, bboxes):
    # return -1 if dummy player
    if tracker_id not in bboxes:
        return -1
    return closest_coords(event["start_time"], bboxes[tracker_id])["team"]


def cartesian_distance(x1, y1, x2, y2):
    x1 *= PITCH_LENGTH
    x2 *= PITCH_LENGTH
    y1 *= PITCH_WIDTH
    y2 *= PITCH_WIDTH
    return ((x1-x2)**2 + (y1-y2)**2)**(0.5)


def closest_coords(timestamp, coords):
    # finds the player coordinates at the closest time to the timestamp
    if len(coords) == 0:
        return {"timestamp": -1, "x": 0, "y": 0, "team": 0}
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

def time_format(seconds):
    mins = int(seconds//60)
    seconds = int(seconds - mins*60)
    return f"{mins}:{str(seconds).zfill(2)}"