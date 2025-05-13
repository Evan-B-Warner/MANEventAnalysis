

def classify_duel(event):
    tags = [event["subtype"].replace(" ", "_")]
    if event["subtype"] == "possessive":
        if event["result"] == "lost_ball":
            tags.append("unsuccessful_duel")
            tags.append("unsusccessful_dribble")
        else:
            tags.append("successful_duel")
        if event["result"] == "dribble":
            tags.append("successful_dribble")
    return tags
