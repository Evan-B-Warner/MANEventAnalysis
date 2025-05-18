
def classify_infraction(event):
    tags = []
    event_subtype = event["subtype"]
    event_result = event["result"]
    if event_subtype == "free kick":
        tags.append("foul")
    elif event_subtype == "penalty":
        tags.append("penalty")
    if event_result == "yellow card":
        tags.append("yellow_card")
    elif event_result == "red card":
        tags.append("red card")
    return tags