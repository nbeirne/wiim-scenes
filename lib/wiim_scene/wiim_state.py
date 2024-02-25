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
    def __init__(self, player_status, player_output_state, player_airplay_speakers):
        self.state = parse_current_state(self, player_status, player_output_state, player_airplay_speakers)


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

    return schema.normalize_schema(state_spec, state) # validate that we produced a proper state

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



