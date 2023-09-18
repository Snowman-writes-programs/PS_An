from flask import request

from constants import RLV2_JSON_PATH, USER_JSON_PATH
from utils import read_json, write_json


def rlv2GiveUpGame():
    return {"result": "ok", "playerDataDelta": {"modified": {"rlv2": {"current": {"player": None, "record": None, "map": None, "troop": None, "inventory": None, "game": None, "buff": None, "module": None}}}, "deleted": {}}}


def rlv2CreateGame():
    request_data = request.get_json()

    theme = request_data["theme"]
    mode = request_data["mode"]
    mode_grade = request_data["modeGrade"]

    if theme == "rogue_1":
        band = "rogue_1_band_1"
        ending = "ro_ending_1"
    elif theme == "rogue_2":
        band = "rogue_2_band_1"
        ending = "ro2_ending_1"

    rlv2 = {
        "player": {
            "state": "INIT",
            "property": {
                "exp": 0,
                "level": 1,
                "maxLevel": 10,
                "hp": {
                    "current": 4,
                    "max": 0
                },
                "gold": 8,
                "shield": 0,
                "capacity": 6,
                "population": {
                    "cost": 0,
                    "max": 6
                },
                "conPerfectBattle": 0
            },
            "cursor": {
                "zone": 0,
                "position": None
            },
            "trace": [],
            "pending": [
                {
                    "index": "e_0",
                    "type": "GAME_INIT_RELIC",
                    "content": {
                        "initRelic": {
                            "step": [
                                1,
                                3
                            ],
                            "items": {
                                "0": {
                                    "id": band,
                                    "count": 1
                                }
                            }
                        }
                    }
                },
                {
                    "index": "e_1",
                    "type": "GAME_INIT_RECRUIT_SET",
                    "content": {
                        "initRecruitSet": {
                            "step": [
                                2,
                                3
                            ],
                            "option": [
                                "recruit_group_1"
                            ]
                        }
                    }
                },
                {
                    "index": "e_2",
                    "type": "GAME_INIT_RECRUIT",
                    "content": {
                        "initRecruit": {
                            "step": [
                                3,
                                3
                            ],
                            "tickets": [],
                            "showChar": [],
                            "team": None
                        }
                    }
                }
            ],
            "status": {
                "bankPut": 0
            },
            "toEnding": ending,
            "chgEnding": False
        },
        "record": {
            "brief": None
        },
        "map": {
            "zones": {}
        },
        "troop": {
            "chars": {},
            "expedition": [],
            "expeditionReturn": None,
            "hasExpeditionReturn": False
        },
        "inventory": {
            "relic": {},
            "recruit": {},
            "trap": None,
            "consumable": {}
        },
        "game": {
            "mode": mode,
            "predefined": None,
            "theme": theme,
            "outer": {
                "support": False
            },
            "start": 1695000000,
            "modeGrade": mode_grade,
            "equivalentGrade": 0
        },
        "buff": {
            "tmpHP": 0,
            "capsule": None,
            "squadBuff": []
        },
        "module": {}
    }

    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2ChooseInitialRelic():
    rlv2 = read_json(RLV2_JSON_PATH)
    band = rlv2["player"]["pending"][0]["content"]["initRelic"]["items"]["0"]["id"]
    rlv2["player"]["pending"] = rlv2["player"]["pending"][1:]
    rlv2["inventory"]["relic"]["r_0"] = {
        "index": "r_0",
        "id": band,
        "count": 1,
        "ts": 1695000000
    }
    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2SelectChoice():
    rlv2 = read_json(RLV2_JSON_PATH)

    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2ChooseInitialRecruitSet():
    rlv2 = read_json(RLV2_JSON_PATH)

    theme = rlv2["game"]["theme"]
    if theme == "rogue_1":
        ticket = "rogue_1_recruit_ticket_all"
    elif theme == "rogue_2":
        ticket = "rogue_2_recruit_ticket_all"
    rlv2["player"]["pending"] = rlv2["player"]["pending"][1:]
    for i in range(3):
        rlv2["player"]["pending"][0]["content"]["initRecruit"]["tickets"].append(
            f"t_{i+1}")
        rlv2["inventory"]["recruit"][f"t_{i+1}"] = {
            "index": f"t_{i+1}",
            "id": ticket,
            "state": 0,
            "list": [],
            "result": None,
            "ts": 1695000000,
            "from": "initial",
            "mustExtra": 0,
            "needAssist": True
        }

    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def getNextPendingIndex(rlv2):
    d = set()
    for e in rlv2["player"]["pending"]:
        d.add(int(e["index"][2:]))
    i = 1
    while i in d:
        i += 1
    return f"e_{i}"


def rlv2ActiveRecruitTicket():
    request_data = request.get_json()
    ticket_id = request_data["id"]

    rlv2 = read_json(RLV2_JSON_PATH)
    pending_index = getNextPendingIndex(rlv2)
    rlv2["player"]["pending"].insert(
        0, {
            "index": pending_index,
            "type": "RECRUIT",
            "content": {
                    "recruit": {
                        "ticket": ticket_id
                    }
            }
        }
    )
    chars = list(
        read_json(USER_JSON_PATH)["user"]["troop"]["chars"].values()
    )
    for i, char in enumerate(chars):
        char.update(
            {
                "instId": str(i),
                "type": "NORMAL",
                "upgradeLimited": False,
                "upgradePhase": 1,
                "isUpgrade": False,
                "isCure": False,
                "population": 0,
                "charBuff": [],
                "troopInstId": "0"
            }
        )
    rlv2["inventory"]["recruit"][ticket_id]["state"] = 1
    rlv2["inventory"]["recruit"][ticket_id]["list"] = chars
    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def getNextCharId(rlv2):
    i = 1
    while str(i) in rlv2["troop"]["chars"]:
        i += 1
    return str(i)


def rlv2RecruitChar():
    request_data = request.get_json()
    ticket_id = request_data["ticketIndex"]
    option_id = int(request_data["optionId"])

    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["pending"].pop(0)
    char_id = getNextCharId(rlv2)
    char = rlv2["inventory"]["recruit"][ticket_id]["list"][option_id]
    char["instId"] = char_id
    rlv2["inventory"]["recruit"][ticket_id]["state"] = 2
    rlv2["inventory"]["recruit"][ticket_id]["list"] = []
    rlv2["inventory"]["recruit"][ticket_id]["result"] = char
    rlv2["troop"]["chars"][char_id] = char
    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2CloseRecruitTicket():
    request_data = request.get_json()
    ticket_id = request_data["id"]

    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["pending"].pop(0)
    rlv2["inventory"]["recruit"][ticket_id]["state"] = 2
    rlv2["inventory"]["recruit"][ticket_id]["list"] = []
    rlv2["inventory"]["recruit"][ticket_id]["result"] = None
    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2FinishEvent():
    rlv2 = read_json(RLV2_JSON_PATH)

    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data


def rlv2MoveAndBattleStart():
    rlv2 = read_json(RLV2_JSON_PATH)

    write_json(rlv2, RLV2_JSON_PATH)

    data = {
        "playerDataDelta": {
            "modified": {
                "rlv2": {
                    "current": rlv2,
                }
            },
            "deleted": {}
        }
    }

    return data
