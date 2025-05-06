from common_utils import cartesian_distance

def is_progressive_pass(passer_x, passer_y, receiver_x, receiver_y):
    start_distance_from_goal = cartesian_distance(passer_x, passer_y, 1, 0.5)
    end_distance_from_goal = cartesian_distance(receiver_x, receiver_y, 1, 0.5)
    distance = end_distance_from_goal - start_distance_from_goal
    return (
        (passer_x <= 0.5 and receiver_x <= 0.5 and distance >= 30) or
        (passer_x <= 0.5 and receiver_x > 0.5 and distance >= 15) or
        (passer_x > 0.5 and receiver_x > 0.5 and distance >= 10)
    )


def is_final_third_pass(passer_x, receiver_x):
    # check if the pass is into either final third
    return (
        (passer_x <= 0.66 and receiver_x > 0.66) or # pass into "right" final third
        (passer_x >= 0.33 and receiver_x < 0.33) # pass into "left" final third
    )


def is_penalty_area_pass(passer_x, passer_y, receiver_x, receiver_y):
    # check if pass is into either penalty area
    into_left_penalty_area = (
        (passer_x > 0.2 or passer_y < 0.25 or passer_y > 0.75) and # passer is outside penalty area
        (receiver_x <= 0.2 and receiver_y >= 0.25 and receiver_y <= 0.75) # receiver is inside area
    )
    into_right_penalty_area = (
        (passer_x < 0.8 or passer_y < 0.25 or passer_y > 0.75) and # passer is outside penalty area
        (receiver_x >= 0.8 and receiver_y >= 0.25 and receiver_y <= 0.75) # receiver is inside area
    )
    return into_left_penalty_area or into_right_penalty_area


def classify_pass(event, passer_x, passer_y, receiver_x, receiver_y):
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
    if is_progressive_pass(passer_x, passer_y, receiver_x, receiver_y):
        tags.append("progressive_pass")
    if is_final_third_pass(passer_x, receiver_x):
        tags.append("final_third_pass")
    if is_penalty_area_pass(passer_x, passer_y, receiver_x, receiver_y):
        tags.append("penalty_area_pass")
    return tags