#!/usr/bin/env python3

import time
import json

from util.json_normalizer import ValidationError, normalize_data

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
        return normalize_data(command_spec, commands)

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


if __name__ == '__main__':
    class Cont:
        def cont_cmd(self, a):
            print("cont_cmd {0}".format(a))

    commands = [
        { "cmd": "print" },
        { "cmd": "cont_cmd", "args": [1] },
        "print",
        { "cmd": "cont_cmd", "args": [1] },
    ]
    scene = CommandRunner(Cont(), commands)

    validated = scene.is_valid()
    if validated is not None:
        print("invalid commands: {0}".format(validated))
        exit(1)

    scene.run()


