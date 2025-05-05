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


def classify_pass(event, passer_x, passer_y, receiver_x, receiver_y):
    # crosses only have one tag
    if event["type"] == "cross":
        return ["cross"]
    
    # otherwise determine tags
    tags = []
    distance = cartesian_distance(passer_x, passer_y, receiver_x, receiver_y)
    if distance < 40:
        tags.append("short_pass")
    elif distance >= 40:
        tags.append("long_pass")
    elif is_progressive_pass(passer_x, passer_y, receiver_x, receiver_y):
        tags.append("progressive_pass")
    elif passer_x <= 0.66 and receiver_x > 0.66:
        tags.append("final_third_pass")
    elif receiver_x > 0.8 and (receiver_y > 0.25 or receiver_y < 0.75):
        tags.append("penalty_area_pass")
    return tags