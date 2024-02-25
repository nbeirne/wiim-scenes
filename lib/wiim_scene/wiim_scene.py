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
    def __init__(self, scene):
        self.scene = schema.normalize_schema(scene_spec, scene)

    def output_mode(self):
        if "output" in self.scene and "mode" in self.scene["output"]:
            return self.scene["output"]["mode"]
        return None

