from common_utils import check_team


def possession_changed(event, bboxes):
    event_type = event["type"]
    participants = event["participants"]
    if event_type == "pass":
        start = participants["passer"]
        end = participants["receiver"]
        start_team = check_team(event, start, bboxes)
        end_team = check_team(event, end, bboxes)
        return start_team != end_team, end_team
    elif event_type == "shot":
        start = participants["shooter"]
        end = participants["blocker"]
        start_team = check_team(event, start, bboxes)
        end_team = check_team(event, end, bboxes)
        return start_team != end_team, end_team
    elif event_type == "duel" and event["result"] == "lost ball":
        return True, check_team(event, participants["defensive"], bboxes)
    return False, None


def retained_possession(team, events, bboxes):
    for event in events:
        event_type = event["type"]
        # check for passes, shots, or carries for same team
        if (
            (event_type == "pass" and check_team(event, event["participants"]["passer"], bboxes) == team) or 
            (event_type == "shot" and check_team(event, event["participants"]["shooter"], bboxes) == team) or 
            (event_type == "carry" and check_team(event, event["participants"]["carrier"], bboxes) == team)
        ):
            return True
        # pass, shots, and carries by other team show possession was not retained
        # clearances also show possession is not retained
        elif event_type in ["pass", "shot", "carry", "clearance"]:
            return False
    return False



def classify_losses_and_interceptions(event, bboxes):
    # constants
    tags = []
    event_type = event["type"]

    # if event is a loss of possession, this is a loss
    # loss can occur from a duel, pass, shot, or infraction
    if event_type in ["pass", "shot", "duel"]:
        changed, _ = possession_changed(event, bboxes)
        if changed:
            tags.append("loss")
            # check if the loss results in an interception
            if event_type in ["pass", "shot"]:
                tags.append("interception")
    return tags


def classify_recoveries(events, bboxes):
    recoveries = {}
    for i in range(len(events)):
        event = events[i]
        if event["type"] in ["pass", "shot", "duel"]:
            changed, new_team = possession_changed(event)
            if changed and retained_possession(new_team, events[i+1:], bboxes):
                recoveries[event["event_id"]] = "recovery"
    return recoveries
