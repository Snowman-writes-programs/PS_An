from faketime import time

from flask import request

from constants import CONFIG_PATH, CRISIS_JSON_BASE_PATH, RUNE_JSON_PATH, CRISIS_V2_JSON_BASE_PATH
from utils import read_json, write_json

def crisisV2_getInfo():
    selected_crisis = read_json(CONFIG_PATH)[
        "crisisV2Config"
    ]["selectedCrisis"]
    if selected_crisis:
        rune = read_json(
            f"{CRISIS_V2_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf-8"
        )
    else:
        rune = {
            "info": {},
            "ts": 1700000000,
            "playerDataDelta": {
                "modified": {},
                "deleted": {}
            }
        }
    return rune


def crisisV2_battleStart():
    request_data = request.get_json()
    battle_data = {
        "mapId": request_data["mapId"],
        "runeSlots": request_data["runeSlots"]
    }
    write_json(battle_data, RUNE_JSON_PATH)
    return {"result": 0, "battleId": "abcdefgh-1234-5678-a1b2c3d4e5f6", "playerDataDelta": {"modified": {}, "deleted": {}}}


def crisisV2_battleFinish():
    battle_data = read_json(RUNE_JSON_PATH)
    mapId = battle_data["mapId"]
    runeSlots = battle_data["runeSlots"]
    scoreCurrent = [0, 0, 0, 0, 0, 0]
    selected_crisis = read_json(CONFIG_PATH)[
        "crisisV2Config"
    ]["selectedCrisis"]
    rune = read_json(
        f"{CRISIS_V2_JSON_BASE_PATH}{selected_crisis}.json", encoding="utf-8"
    )

    nodes = {}
    for slot in rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"]:
        if not slot.startswith("node_"):
            continue
        nodeData = rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"][slot]
        slotPackId = nodeData["slotPackId"]
        if not slotPackId:
            continue
        if slotPackId not in nodes:
            nodes[slotPackId] = {}
        if nodeData["mutualExclusionGroup"]:
            mutualExclusionGroup = nodeData["mutualExclusionGroup"]
        else:
            mutualExclusionGroup = slot
        if mutualExclusionGroup not in nodes[slotPackId]:
            nodes[slotPackId][mutualExclusionGroup] = {}
        if "runeId" in nodeData:
            runeId = rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"][slot]["runeId"]
            if runeId:
                runeData = rune["info"]["mapDetailDataMap"][mapId]["runeDataMap"][runeId]
                score = runeData["score"]
            else:
                score = 0
        else:
            score = 0
        nodes[slotPackId][mutualExclusionGroup][slot] = score

    slots = set(runeSlots)
    for slotPackId in nodes:
        flag = True
        for mutualExclusionGroup in nodes[slotPackId]:
            score_max = 0
            for slot in nodes[slotPackId][mutualExclusionGroup]:
                score_max = max(
                    score_max,  nodes[slotPackId][mutualExclusionGroup][slot]
                )
            flag2 = False
            for slot in nodes[slotPackId][mutualExclusionGroup]:
                if nodes[slotPackId][mutualExclusionGroup][slot] != score_max:
                    continue
                if slot in slots:
                    flag2 = True
                    break
            if not flag2:
                flag = False
                break
        if flag:
            bagData = rune["info"]["mapDetailDataMap"][mapId]["bagDataMap"][slotPackId]
            scoreCurrent[bagData["dimension"]] += bagData["rewardScore"]

    for slot in runeSlots:
        nodeData = rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"][slot]
        if "runeId" in nodeData:
            runeId = rune["info"]["mapDetailDataMap"][mapId]["nodeDataMap"][slot]["runeId"]
            runeData = rune["info"]["mapDetailDataMap"][mapId]["runeDataMap"][runeId]
            scoreCurrent[runeData["dimension"]] += runeData["score"]
    return {"result": 0, "mapId": mapId, "runeSlots": runeSlots, "isNewRecord": False, "scoreRecord": [0, 0, 0, 0, 0, 0], "scoreCurrent": scoreCurrent, "runeCount": [0, 0], "commentNew": [], "commentOld": [], "ts": 1700000000, "playerDataDelta": {"modified": {}, "deleted": {}}}