from common_utils import cartesian_distance, closest_coords

def is_progressive_pass(passer_team, receiver_team, passer_x, passer_y, receiver_x, receiver_y):
    distance_change_from_right_goal = cartesian_distance(receiver_x, receiver_y, 1, 0.5) - cartesian_distance(passer_x, passer_y, 1, 0.5)
    distance_change_from_left_goal = cartesian_distance(receiver_x, receiver_y, 0, 0.5) - cartesian_distance(passer_x, passer_y, 0, 0.5)
    progressive_pass_right = (
        passer_team == 0 and receiver_team == 0 and
        (
            (passer_x <= 0.5 and receiver_x <= 0.5 and distance_change_from_right_goal >= 30) or
            (passer_x <= 0.5 and receiver_x > 0.5 and distance_change_from_right_goal >= 15) or
            (passer_x > 0.5 and receiver_x > 0.5 and distance_change_from_right_goal >= 10)
        )
    )
    progressive_pass_left = (
        passer_team == 1 and receiver_team == 1 and
        (
            (passer_x >= 0.5 and receiver_x >= 0.5 and distance_change_from_left_goal >= 30) or
            (passer_x >= 0.5 and receiver_x < 0.5 and distance_change_from_left_goal >= 15) or
            (passer_x < 0.5 and receiver_x < 0.5 and distance_change_from_left_goal >= 10)
        )
    )
    return progressive_pass_left or progressive_pass_right


def is_final_third_pass(passer_team, receiver_team, passer_x, receiver_x):
    # check if the pass is into either final third
    return (
        (
            (passer_x <= 0.66 and receiver_x > 0.66) and # pass into "right" final third
            (passer_team == 0 and receiver_team == 0) # at least one member is attacking right
        ) or 
        (
            (passer_x >= 0.33 and receiver_x < 0.33) and # pass into "left" final third
            (passer_team == 1 and receiver_team == 1) # at least one member is attacking left
        )
    )


def is_penalty_area_pass(passer_team, receiver_team, passer_x, passer_y, receiver_x, receiver_y):
    # check if pass is into either penalty area
    into_left_penalty_area = (
        (passer_x > 0.2 or passer_y < 0.25 or passer_y > 0.75) and # passer is outside penalty area
        (receiver_x <= 0.2 and receiver_y >= 0.25 and receiver_y <= 0.75) and # receiver is inside area
        (passer_team == 1 and receiver_team == 1) # at least one member is attacking to the left
    )
    into_right_penalty_area = (
        (passer_x < 0.8 or passer_y < 0.25 or passer_y > 0.75) and # passer is outside penalty area
        (receiver_x >= 0.8 and receiver_y >= 0.25 and receiver_y <= 0.75) and # receiver is inside area
        (passer_team == 0 and receiver_team == 0) # at least one member is attacking to the right
    )
    return into_left_penalty_area or into_right_penalty_area


def get_last_man_x(event_time, passer_team, bboxes):
    # get the player with farthest x_coord from the defending team
    min_x, max_x = 2, -1
    for tracker_id in bboxes:
        current_bboxes = bboxes[tracker_id]
        if current_bboxes[0]["timestamp"] > event_time or current_bboxes[-1]["timestamp"] < event_time:
            continue
        current_coords = closest_coords(event_time, current_bboxes)
        if current_coords["team"] != passer_team:
            min_x = min(min_x, current_coords["x"])
            max_x = max(max_x, current_coords["x"])
    return max_x if passer_team == 0 else min_x
    

def is_through_pass(event, passer_team, bboxes, passer_x, receiver_x):
    last_man_x = get_last_man_x(event["start_time"]+1, passer_team, bboxes)
    return (
        (passer_team == 0 and passer_x < last_man_x - 0.05 and receiver_x > last_man_x + 0.05) or # through pass to the right
        (passer_team == 1 and passer_x > last_man_x - 0.05 and receiver_x < last_man_x + 0.05) # through pass to the left
    )


def classify_pass(event, passer_team, receiver_team, passer_x, passer_y, receiver_x, receiver_y, bboxes):
    # only successful passes have a tag
    if passer_team != receiver_team:
        return []

    # crosses only have one tag
    if event["subtype"] == "cross":
        return ["cross"]
    
    # otherwise determine granular pass tags
    tags = []
    distance = cartesian_distance(passer_x, passer_y, receiver_x, receiver_y)
    if distance < 40:
        tags.append("short_pass")
    else:
        tags.append("long_pass")
    if is_progressive_pass(passer_team, receiver_team, passer_x, passer_y, receiver_x, receiver_y):
        tags.append("progressive_pass")
    if is_final_third_pass(passer_team, receiver_team,passer_x, receiver_x):
        tags.append("final_third_pass")
    if is_penalty_area_pass(passer_team, receiver_team,passer_x, passer_y, receiver_x, receiver_y):
        tags.append("penalty_area_pass")
    if is_through_pass(event, passer_team, bboxes, passer_x, receiver_x):
        tags.append("through_pass")
    return tags