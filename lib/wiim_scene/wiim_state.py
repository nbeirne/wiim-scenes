from copy import deepcopy

from . import wiim_device
from ..util import schema

# define what we expect state to look like.
# side note: a state is a stricter version of a scene

state_spec = {
    "type": "dict",
    "keys": {
        "volume": {
            "type": "int",
            "required": True,
        },
        "input": {
            "type": "dict",
            "required": True,
            "keys": {
                "mode": {
                    "type": "str",
                    "required": True,
                },
            },
        },
        "output": {
            "type": "dict",
            "required": True,
            "keys": {
                "mode": {
                    "type": "str",
                    "required": True,
                },
                "airplay": {
                    "type": "list",
                    "items": {
                        "type": "dict",
                        "keys": {
                            "device": {
                                "type": "str",
                                "required": True,
                            },
                            "name": {
                                "type": "str",
                                "required": True,
                            },
                            "id": {
                                "type": "str",
                                "required": True,
                            },
                            "selected": {
                                "type": "bool",
                                "required": True,
                            },
                            "volume": {
                                "type": "int",
                                "required": True,
                            },
                        },
                    },
                },
            },
        },
    },
}

class WiimState:
    def __init__(self, state):
        self.state = schema.normalize_schema(state_spec, state)

    def apply_scene(self, scene):
        scene = scene.scene
        new_state = deepcopy(self.state)

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

            if "airplay" in self.state["output"] and "airplay" in scene["output"]:
                new_state["output"]["airplay"] = apply_airplay_queries(self.state["output"]["airplay"], scene["output"]["airplay"])

            elif "airplay" in scene["output"]:
                new_state["output"]["airplay"] = scene["output"]["airplay"]

        return new_state

    def does_scene_match(self, scene, match_volume=False):
        if match_volume and "volume" in scene and self.state["volume"] != scene["volume"]:
            return False

        if "input" in scene and self.state["input"] != scene["input"]:
            return False

        if "output" in scene:
            if self.state["output"]["mode"] != scene["output"]["mode"]:
                return False
            if self.state["output"]["mode"] == "airplay" and "airplay" in self.state["output"] and "airplay" in scene["output"]:
                if not does_airplay_devices_match_queries(self.state["output"]["airplay"], scene["output"]["airplay"], match_volume):
                    return False

        return True



# current scene creation from external info

def parse_current_state(player_status, player_output_state, player_airplay_speakers=None):
    state = {
        "status": player_status["status"],
        "volume": int(player_status["vol"]),
        "input": {
            "mode": wiim_device.parse_input_mode(player_status["mode"])
        },
        "output": {
            "mode": wiim_device.parse_output_state(player_output_state),
            **create_airplay_list(player_output_state, player_airplay_speakers)
        },
    }

    return WiimState(state)

def filter_airplay_info(airplay_device):
    airplay_device_keys = set(["id", "device", "name", "selected", "volume" ])

    airplay_device = deepcopy(airplay_device)
    keys_to_remove = set(airplay_device.keys()) - airplay_device_keys
    for key in keys_to_remove:
        airplay_device.pop(key)

    # group_id, has_password, needs_auth_key, requires_auth
    return airplay_device


def create_airplay_list(player_output_state, player_airplay_speakers):
    if player_airplay_speakers is None:
        return {}

    return  {
        "airplay": list(map(filter_airplay_info, player_airplay_speakers))
    }



# application

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


# querying

def does_airplay_device_match_query(query, airplay_device):
    match_fields = ["id", "name", "type", "device"]
    for field in match_fields:
        if field in query and query[field] != airplay_device[field]:
            return False
    return True

def does_airplay_devices_match_queries(airplay_devices, airplay_queries, match_volume):
    devices = {}

    for airplay_device in airplay_devices:
        for query in airplay_queries:
            if does_airplay_device_match_query(query, airplay_device):
                if query["selected"] != airplay_device["selected"]:
                    devices[airplay_device["id"]] = False
                elif match_volume and "volume" in query and query["volume"] != airplay_device["volume"]:
                    devices[airplay_device["id"]] = False
                else:
                    devices[airplay_device["id"]] = True

    return all(devices.values())
