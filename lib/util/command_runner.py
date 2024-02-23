#!/usr/bin/env python3

import time
import json

from ..util import json_normalizer

command_spec = {
    "type": "list",
    "items": {
        "type": "dict",
        "default_key": "cmd",
        "keys": {
            "cmd": {
                "type": "str",
                "required": True,
            },
            "args": {
                "type": "list",
                "allow_single_item": True,
                "default_value": [],
                "required": True,
            },
        },
    },
}

class CommandRunner:
    def __init__(self, controller, commands):
        self.controller = controller
        self.commands = commands
        self.builtin_commands = {
            "sleep": lambda args: time.sleep(*args),
            "print": lambda args: print(*args),
        }

    def normalized_commands(self, commands):
        return json_normalizer.normalize_data(command_spec, commands)

    def is_valid(self):
        commands = None
        try: 
            commands = self.normalized_commands(self.commands)
        except ValidationError as error: 
            return getattr(error, 'message', str(error))

        for command in commands:
            cmd = command["cmd"]
            args = command["args"]

            if cmd in self.builtin_commands: 
                continue
            if getattr(self.controller, cmd, None) is not None:
                continue

            return "command not found: {0}".format(cmd)

        return None

    def run(self):
        commands = self.normalized_commands(self.commands)
        for command in commands:
            cmd = command["cmd"]
            args = command["args"]

            if cmd in self.builtin_commands: 
                self.builtin_commands[cmd](args)
            else:
                func = getattr(self.controller, cmd)
                if func != None:
                    func(*args)
                else:
                    print("unknown command: %s" % command)

