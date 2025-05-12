
from common_utils import closest_coords


def check_team(event, tracker_id, bboxes):
    return closest_coords(event["start_time"], bboxes[tracker_id])["team"]


def classify_assists(events, bboxes):
    assists = {
        "shot_assists": [],
        "assists": [],
        "second_assists": [],
        "third_assists": [],
    }
    for event_id in events:
        event = events[event_id]
        if event["type"] == "shot":
            is_goal = event["result"] == "goal"
            # check the three previous pass events, stopping on possession loss, for assists
            scoring_team = check_team(event, event["participants"]["shooter"], bboxes)
            pass_counter = 0
            assist_counter = 0
            while True:
                pass_counter += 1
                index = event_id - pass_counter
                # check for out of bounds
                if index not in events < 0:
                    break
                current_event = events[index]
                # check for loss of possession
                if (
                    current_event["type"] in ["shot", "infraction", "clearance"] or # these events cause possession loss
                    (
                        current_event["type"] == "duel" and 
                        (
                            check_team(current_event, current_event["participants"]["offensive"], bboxes) != scoring_team or # the possessing player in the duel is on the other team
                            current_event["result"] == "lost ball" # if the ball is lost, either the scoring team lost possession, or the above case
                        ) 
                    ) or
                    (
                        current_event["type"] == "pass" and 
                        check_team(current_event, current_event["participants"]["receiver"], bboxes) != scoring_team # the other team receives a bed
                    )
                ):
                    break

                # otherwise if this event is a pass, classify it as an assist
                if current_event["type"] == "pass":
                    assister = current_event["participants"]["passer"]
                    if assist_counter == 0:
                        if is_goal:
                            assists["assists"].append({"event_id": index, "assister": assister})
                        else:
                            assists["shot_assists"].append({"event_id": index, "assister": assister})
                    elif assist_counter == 1:
                        assists["second_assists"].append({"event_id": index, "assister": assister})
                    elif assist_counter == 2:
                        assists["third_assists"].append({"event_id": index, "assister": assister})
                    assist_counter += 1

                # break if we have already found all three assists or one assist for just a shot
                if assist_counter == 3 or (assist_counter == 1 and not is_goal):
                    break
    return assists
                