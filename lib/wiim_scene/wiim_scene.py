from copy import deepcopy

from ..util import schema

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


class WiimScene:
    def __init__(self, json_scene):
        self.scene = normalize_scene(json_scene)

    def does_state_match(self, state):
        scene = self.scene
        if "volume" in scene and state["volume"] != scene["volume"]:
            return False

        if "input" in scene and state["input"] != scene["input"]:
            return False

        if "output" in scene:
            if state["output"]["mode"] != scene["output"]["mode"]:
                return False
            if state["output"]["mode"] == "airplay" and "airplay" in state["output"] and "airplay" in scene["output"]:
                if not does_airplay_devices_match_queries(state["output"]["airplay"], scene["output"]["airplay"]):
                    return False

        return True

    def output_mode(self):
        if "output" in self.scene and "mode" in self.scene["output"]:
            return self.scene["output"]["mode"]
        return None

    def apply_scene_over_state(self, state):
        scene = self.scene
        new_state = deepcopy(state)

        if "volume" in scene:
            new_state["volume"] = scene["volume"]

        if "input" in scene:
            if "mode" in scene["input"]:
                new_state["input"]["mode"] = scene["input"]["mode"]
        if "output" in scene:
            if "mode" in scene["output"]:
                new_state["output"]["mode"] = scene["output"]["mode"]

            if "volume" in scene["output"]:
                new_state["output"]["volume"] = scene["output"]["volume"]

            if "airplay" in state["output"] and "airplay" in scene["output"]:
                new_state["output"]["airplay"] = apply_airplay_queries(state["output"]["airplay"], scene["output"]["airplay"])

            elif "airplay" in scene["output"]:
                new_state["output"]["airplay"] = scene["output"]["airplay"]

        return new_state


## normalization helpers

def normalize_scene(orig_scene):
    return schema.normalize_schema(scene_spec, orig_scene)

# Scene merging + applying a scene over another one

def does_airplay_device_match_query(query, airplay_device):
    match_fields = ["id", "name", "type", "device"]
    for field in match_fields:
        if field in query and query[field] != airplay_device[field]:
            return False
    return True

def apply_airplay_queries(airplay_devices, airplay_queries):
    airplay_devices = deepcopy(airplay_devices)
    new_airplay_devices = []
    for airplay_device in airplay_devices:
        for query in airplay_queries:
            if does_airplay_device_match_query(query, airplay_device):
                airplay_device = {
                    **airplay_device,
                    **query
                }
        new_airplay_devices.append(airplay_device)
    return new_airplay_devices

def does_airplay_devices_match_queries(airplay_devices, airplay_queries):
    devices = {}

    for airplay_device in airplay_devices:
        for query in airplay_queries:
            if does_airplay_device_match_query(query, airplay_device):
                if query["selected"] != airplay_device["selected"]:
                    devices[airplay_device["id"]] = False
                elif "volume" in query and query["volume"] != airplay_device["volume"]:
                    devices[airplay_device["id"]] = False
                else:
                    devices[airplay_device["id"]] = True

    return all(devices.values())
