from flask import request

from constants import RLV2_JSON_PATH, USER_JSON_PATH, RL_TABLE_URL, CONFIG_PATH
from utils import read_json, write_json, decrypt_battle_data
from core.function.update import updateData
from copy import deepcopy


def rlv2GiveUpGame():
    return {"result": "ok", "playerDataDelta": {"modified": {"rlv2": {"current": {"player": None, "record": None, "map": None, "troop": None, "inventory": None, "game": None, "buff": None, "module": None}}}, "deleted": {}}}


def getChars():
    user_data = read_json(USER_JSON_PATH)
    chars = [
        user_data["user"]["troop"]["chars"][i] for i in user_data["user"]["troop"]["chars"]
    ]
    for i in range(len(chars)):
        char = chars[i]
        if char["evolvePhase"] == 2:
            char_alt = deepcopy(char)
            char_alt["evolvePhase"] = 1
            char_alt["level"] -= 10
            if len(char["skills"]) == 3:
                char_alt["defaultSkillIndex"] = 1
                char_alt["skills"].pop()
            for skill in char_alt["skills"]:
                skill["specializeLevel"] = 0
            char_alt["currentEquip"] = None
            char_alt["equip"] = {}
            chars.append(char_alt)
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
        if char["evolvePhase"] < 2:
            char["upgradePhase"] = 0
    return chars


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
    elif theme == "rogue_3":
        band = "rogue_3_band_1"
        ending = "ro3_ending_1"

    rlv2 = {
        "player": {
            "state": "INIT",
            "property": {
                "exp": 0,
                "level": 1,
                "maxLevel": 10,
                "hp": {
                    "current": 50,
                    "max": 0
                },
                "gold": 8,
                "shield": 0,
                "capacity": 13,
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

    # too large, do not send it every time
    config = read_json(CONFIG_PATH)
    if config["rlv2Config"]["allChars"]:
        if theme == "rogue_1":
            ticket = "rogue_1_recruit_ticket_all"
        elif theme == "rogue_2":
            ticket = "rogue_2_recruit_ticket_all"
        elif theme == "rogue_3":
            ticket = "rogue_3_recruit_ticket_all"
        chars = getChars()
        for i, char in enumerate(chars):
            ticket_id = f"t_{i}"
            char_id = str(i+1)
            char["instId"] = char_id
            rlv2["inventory"]["recruit"][ticket_id] = {
                "index": f"t_{i}",
                "id": ticket,
                "state": 2,
                "list": [],
                "result": char,
                "ts": 1695000000,
                "from": "initial",
                "mustExtra": 0,
                "needAssist": True
            }
            rlv2["troop"]["chars"][char_id] = char

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
    rlv2["player"]["pending"].pop(0)
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


def addTicket(rlv2, ticket_id):
    theme = rlv2["game"]["theme"]
    if theme == "rogue_1":
        ticket = "rogue_1_recruit_ticket_all"
    elif theme == "rogue_2":
        ticket = "rogue_2_recruit_ticket_all"
    elif theme == "rogue_3":
        ticket = "rogue_3_recruit_ticket_all"
    rlv2["inventory"]["recruit"][ticket_id] = {
        "index": ticket_id,
        "id": ticket,
        "state": 0,
        "list": [],
        "result": None,
        "ts": 1695000000,
        "from": "initial",
        "mustExtra": 0,
        "needAssist": True
    }


def getNextTicketIndex(rlv2):
    d = set()
    for e in rlv2["inventory"]["recruit"]:
        d.add(int(e[2:]))
    config = read_json(CONFIG_PATH)
    if not config["rlv2Config"]["allChars"]:
        i = 0
    else:
        i = 10000-1
    while i in d:
        i += 1
    return f"t_{i}"


def rlv2ChooseInitialRecruitSet():
    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["pending"].pop(0)

    config = read_json(CONFIG_PATH)
    if not config["rlv2Config"]["allChars"]:
        for i in range(3):
            ticket_id = getNextTicketIndex(rlv2)
            addTicket(rlv2, ticket_id)
            rlv2["player"]["pending"][0]["content"]["initRecruit"]["tickets"].append(
                ticket_id
            )

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
    i = 0
    while i in d:
        i += 1
    return f"e_{i}"


def activateTicket(rlv2, ticket_id):
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
    chars = getChars()
    rlv2["inventory"]["recruit"][ticket_id]["state"] = 1
    rlv2["inventory"]["recruit"][ticket_id]["list"] = chars


def rlv2ActiveRecruitTicket():
    request_data = request.get_json()
    ticket_id = request_data["id"]

    rlv2 = read_json(RLV2_JSON_PATH)
    activateTicket(rlv2, ticket_id)
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
    config = read_json(CONFIG_PATH)
    if not config["rlv2Config"]["allChars"]:
        i = 1
    else:
        i = 10000
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


def getMap(theme):
    rlv2_table = updateData(RL_TABLE_URL)
    stages = [i for i in rlv2_table["details"][theme]["stages"]]
    if theme == "rogue_1":
        shop = 8
    elif theme == "rogue_2":
        shop = 4096
    elif theme == "rogue_3":
        shop = 4096
    map = {}
    zone = 1
    j = 0
    while j < len(stages):
        zone_map = {
            "id": f"zone_{zone}",
            "index": zone,
            "nodes": {},
            "variation": []
        }
        nodes_list = [
            [
                {
                    "index": "0",
                    "pos": {
                        "x": 0,
                        "y": 0
                    },
                    "next": [],
                    "type": shop
                }
            ]
        ]
        x_max = 9
        y_max = 3
        x = 0
        y = y_max+1
        while j < len(stages):
            stage = stages[j]
            if y > y_max:
                if x+1 == x_max:
                    break
                nodes_list.append([])
                x += 1
                y = 0
            nodes_list[-1].append(
                {
                    "index": f"{x}0{y}",
                    "pos": {
                        "x": x,
                        "y": y
                    },
                    "next": [],
                    "type": 1,
                    "stage": stage
                }
            )
            y += 1
            j += 1
        x += 1
        nodes_list.append(
            [
                {
                    "index": f"{x}00",
                    "pos": {
                        "x": x,
                        "y": 0
                    },
                    "next": [],
                    "type": shop,
                    "zone_end": True
                }
            ]
        )
        for i, nodes in enumerate(nodes_list):
            if i == 0:
                continue
            nodes_next = [node["pos"] for node in nodes]
            for node in nodes_list[i-1]:
                node["next"] = nodes_next
        nodes_list[0][0]["next"].append(
            {
                "x": x,
                "y": 0
            }
        )
        for nodes in nodes_list:
            for node in nodes:
                zone_map["nodes"][node["index"]] = node
        map[str(zone)] = zone_map
        zone += 1
    return map


def rlv2FinishEvent():
    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["state"] = "WAIT_MOVE"
    rlv2["player"]["cursor"]["zone"] += 1
    rlv2["player"]["pending"] = []
    theme = rlv2["game"]["theme"]
    write_json(rlv2, RLV2_JSON_PATH)

    # too large, do not send it every time
    rlv2["map"]["zones"] = getMap(theme)

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


def getBuffs(rlv2):
    rlv2_table = updateData(RL_TABLE_URL)
    theme = rlv2["game"]["theme"]
    buffs = []

    if rlv2["inventory"]["trap"] is not None:
        item_id = rlv2["inventory"]["trap"]["id"]
        if item_id in rlv2_table["details"][theme]["relics"]:
            buffs += rlv2_table["details"][theme]["relics"][item_id]["buffs"]

    return buffs


def rlv2MoveAndBattleStart():
    request_data = request.get_json()
    x = request_data["to"]["x"]
    y = request_data["to"]["y"]

    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["state"] = "PENDING"
    rlv2["player"]["cursor"]["position"] = {
        "x": x,
        "y": y
    }
    rlv2["player"]["trace"].append(rlv2["player"]["cursor"])
    pending_index = getNextPendingIndex(rlv2)
    buffs = getBuffs(rlv2)
    rlv2["player"]["pending"].insert(
        0,
        {
            "index": pending_index,
            "type": "BATTLE",
            "content": {
                "battle": {
                    "state": 1,
                    "chestCnt": 0,
                    "goldTrapCnt": 0,
                    "diceRoll": [],
                    "boxInfo": {},
                    "tmpChar": [],
                    "sanity": 0,
                    "unKeepBuff": buffs
                }
            }
        }
    )
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


def rlv2BattleFinish():
    request_data = request.get_json()
    battle_data = decrypt_battle_data(request_data["data"], 1672502400)

    rlv2 = read_json(RLV2_JSON_PATH)
    if battle_data["completeState"] != 1:
        rlv2["player"]["pending"].pop(0)
        theme = rlv2["game"]["theme"]
        if theme == "rogue_1":
            ticket = "rogue_1_recruit_ticket_all"
        elif theme == "rogue_2":
            ticket = "rogue_2_recruit_ticket_all"
        elif theme == "rogue_3":
            ticket = "rogue_3_recruit_ticket_all"
        pending_index = getNextPendingIndex(rlv2)
        rlv2["player"]["pending"].insert(
            0,
            {
                "index": pending_index,
                "type": "BATTLE_REWARD",
                "content": {
                    "battleReward": {
                        "earn": {
                            "damage": 0,
                            "hp": 0,
                            "shield": 0,
                            "exp": 0,
                            "populationMax": 0,
                            "squadCapacity": 0,
                            "maxHpUp": 0
                        },
                        "rewards": [
                            {
                                "index": 0,
                                "items": [
                                    {
                                        "sub": 0,
                                        "id": ticket,
                                        "count": 1
                                    }
                                ],
                                "done": 0
                            }
                        ],
                        "show": "1"
                    }
                }
            }
        )
    else:
        rlv2["player"]["state"] = "WAIT_MOVE"
        rlv2["player"]["pending"] = []
        rlv2["player"]["cursor"]["position"]["x"] -= 1
        rlv2["player"]["cursor"]["position"]["y"] = 0
        rlv2["player"]["trace"].pop()
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


def rlv2FinishBattleReward():
    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["state"] = "WAIT_MOVE"
    rlv2["player"]["pending"] = []
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


def getGoods(theme):
    if theme == "rogue_1":
        ticket = "rogue_1_recruit_ticket_all"
        price_id = "rogue_1_gold"
    elif theme == "rogue_2":
        ticket = "rogue_2_recruit_ticket_all"
        price_id = "rogue_2_gold"
    elif theme == "rogue_3":
        ticket = "rogue_3_recruit_ticket_all"
        price_id = "rogue_3_gold"
    goods = [
        {
            "index": "0",
            "itemId": ticket,
            "count": 1,
            "priceId": price_id,
            "priceCount": 0,
            "origCost": 0,
            "displayPriceChg": False,
            "_retainDiscount": 1
        }
    ]
    i = 1
    rlv2_table = updateData(RL_TABLE_URL)
    for j in rlv2_table["details"][theme]["archiveComp"]["relic"]["relic"]:
        goods.append(
            {
                "index": str(i),
                "itemId": j,
                "count": 1,
                "priceId": price_id,
                "priceCount": 0,
                "origCost": 0,
                "displayPriceChg": False,
                "_retainDiscount": 1
            }
        )
        i += 1
    for j in rlv2_table["details"][theme]["archiveComp"]["trap"]["trap"]:
        goods.append(
            {
                "index": str(i),
                "itemId": j,
                "count": 1,
                "priceId": price_id,
                "priceCount": 0,
                "origCost": 0,
                "displayPriceChg": False,
                "_retainDiscount": 1
            }
        )
        i += 1
    return goods


def rlv2MoveTo():
    request_data = request.get_json()
    x = request_data["to"]["x"]
    y = request_data["to"]["y"]

    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["state"] = "PENDING"
    rlv2["player"]["cursor"]["position"] = {
        "x": x,
        "y": y
    }
    theme = rlv2["game"]["theme"]
    goods = getGoods(theme)
    rlv2["player"]["trace"].append(rlv2["player"]["cursor"])
    pending_index = getNextPendingIndex(rlv2)
    rlv2["player"]["pending"].insert(
        0,
        {
            "index": pending_index,
            "type": "SHOP",
            "content": {
                "shop": {
                    "bank": {
                        "open": False,
                        "canPut": False,
                        "canWithdraw": False,
                        "withdraw": 0,
                        "cost": 1
                    },
                    "id": "just_a_shop",
                    "goods": goods,
                    "_done": False
                }
            }
        }
    )
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


def getNextRelicIndex(rlv2):
    d = set()
    for e in rlv2["inventory"]["relic"]:
        d.add(int(e[2:]))
    i = 0
    while i in d:
        i += 1
    return f"r_{i}"


def rlv2BuyGoods():
    request_data = request.get_json()
    select = int(request_data["select"][0])

    rlv2 = read_json(RLV2_JSON_PATH)
    item_id = rlv2["player"]["pending"][0]["content"]["shop"]["goods"][select]["itemId"]
    if item_id.find("_recruit_ticket_") != -1:
        ticket_id = getNextTicketIndex(rlv2)
        addTicket(rlv2, ticket_id)
        activateTicket(rlv2, ticket_id)
    elif item_id.find("_relic_") != -1:
        relic_id = getNextRelicIndex(rlv2)
        rlv2["inventory"]["relic"][relic_id] = {
            "index": relic_id,
            "id": item_id,
            "count": 1,
            "ts": 1695000000
        }
    elif item_id.find("_active_tool_") != -1:
        rlv2["inventory"]["trap"] = {
            "index": item_id,
            "id": item_id,
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


def rlv2LeaveShop():
    rlv2 = read_json(RLV2_JSON_PATH)
    rlv2["player"]["state"] = "WAIT_MOVE"
    rlv2["player"]["pending"] = []
    if rlv2["player"]["cursor"]["position"]["x"] > 0:
        rlv2["player"]["cursor"]["zone"] += 1
        rlv2["player"]["cursor"]["position"] = None
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


def rlv2ChooseBattleReward():
    request_data = request.get_json()
    index = request_data["index"]

    rlv2 = read_json(RLV2_JSON_PATH)
    if index == 0:
        ticket_id = getNextTicketIndex(rlv2)
        addTicket(rlv2, ticket_id)
        activateTicket(rlv2, ticket_id)
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
