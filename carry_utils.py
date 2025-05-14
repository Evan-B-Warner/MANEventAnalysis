from common_utils import cartesian_distance

def classify_carry(event, carrier_team, start_x, start_y, end_x, end_y):
    distance_change_from_right_goal = cartesian_distance(end_x, end_y, 1, 0.5) - cartesian_distance(start_x, start_y, 1, 0.5)
    distance_change_from_left_goal = cartesian_distance(end_x, end_y, 0, 0.5) - cartesian_distance(start_x, start_y, 0, 0.5)
    progressive_run_right = (
        carrier_team == 0 and
        (
            (start_x <= 0.5 and end_x <= 0.5 and distance_change_from_right_goal >= 30) or
            (start_x <= 0.5 and end_x > 0.5 and distance_change_from_right_goal >= 15) or
            (start_x > 0.5 and end_x > 0.5 and distance_change_from_right_goal >= 10)
        )
    ) 
    progressive_run_left = (
        carrier_team == 1 and
        (
            (start_x >= 0.5 and end_x >= 0.5 and distance_change_from_left_goal >= 30) or
            (start_x >= 0.5 and end_x < 0.5 and distance_change_from_left_goal >= 15) or
            (start_x < 0.5 and end_x < 0.5 and distance_change_from_left_goal >= 10)
        )
    )
    return ["progressive_run"] if progressive_run_left or progressive_run_right else []