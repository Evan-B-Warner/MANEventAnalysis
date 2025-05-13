

def classify_shot(event):
    tags = ["shot"]
    if event["subtype"] in ["shot", "free kick"]:
        if event["result"] in ["goal", "save", "reflex save"]:
            tags.append("on_target")
        else:
            tags.append("off_target")
    elif event["subtype"] == "penalty":
        tags.append("penalty")
    if event["result"] == "goal":
        tags.append("goal")
    return tags
