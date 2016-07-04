def createMessageDict(color, message):
    message_dict = {
        "color": color,
        "message": str(message),
        "notify": False,
        "message_format": "text"
        }
    return message_dict
