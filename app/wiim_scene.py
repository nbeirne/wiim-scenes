from copy import deepcopy

import util.json_normalizer as json_normalizer

# Define what we expect a Scene to look like
scene_spec = {
    "type": "dict",
    "keys": {
        "volume": {
            "type": "int",
        },
        "input": {
            "type": "dict",
            "default_key": "mode",
            "keys": {
                "mode": {
                    "type": "str",
                    "required": True,
                },
            },
        },
        "output": {
            "type": "dict",
            "default_key": "mode",
            "keys": {
                "mode": {
                    "type": "str",
                    "required": True,
                },
                "airplay": {
                    "type": "list",
                    "allow_single_item": True,
                    "items": {
                        "type": "dict",
                        "default_key": "name",
                        "keys": {
                            "id": {
                                "type": "str",
                            },
                            "type": {
                                "type": "str",
                            },
                            "device": {
                                "type": "str",
                            },
                            "name": {
                                "type": "str",
                            },
                            "selected": {
                                "type": "bool",
                                "default_value": True,
                                "required": True,
                            },
                            "volume": {
                                "type": "int",
                            },
                        },
                    },
                },
            },
        },
    },
}


## normalization helpers

def normalize_scene(orig_scene):
    return json_normalizer.normalize_data(scene_spec, orig_scene)

# Scene merging + applying a scene over another one

def apply_scene_over_state(state, apply):
    scene = deepcopy(state)

    if "volume" in apply:
        scene["volume"] = apply["volume"]
    if "input" in apply:
        if "mode" in apply["input"]:
            scene["input"]["mode"] = apply["input"]["mode"]
    if "output" in apply:
        if "mode" in apply["output"]:
            scene["output"]["mode"] = apply["output"]["mode"]

        if "airplay" in apply["output"] and "airplay" in scene["output"]:
            scene["output"]["airplay"] = apply_airplay_queries(apply["output"]["airplay"], scene["output"]["airplay"])
        elif "airplay" in apply["output"]:
            scene["output"]["airplay"] = apply["output"]["airplay"]
        #    print("ap")
    return scene

def does_airplay_device_mach_query(query, airplay_device):
    match_fields = ["id", "name", "type", "device"]
    for field in match_fields:
        if field in query and query[field] != airplay_device[field]:
            return False
    return True

def apply_airplay_queries(airplay_queries, airplay_list):
    airplay_list = deepcopy(airplay_list)
    new_airplay_list = []
    for airplay_device in airplay_list:
        for query in airplay_queries:
            if does_airplay_device_mach_query(query, airplay_device):
                airplay_device = {
                    **airplay_device,
                    **query
                }
        new_airplay_list.append(airplay_device)
    return new_airplay_list


