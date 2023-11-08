from flask import request

def CrisisV2Function():

    data = request.data

    data = {
        "crisisV2List": [],
        "playerDataDelta": {
            "modified": {},
            "deleted": {}
        }
    }

    return data