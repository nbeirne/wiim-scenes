#!/usr/bin/env python3

import util.command_runner as command_runner


# TODO: explicit "normalize command" function. Expand text command into cmd, etc
# TODO: explicit "normalize scene" function. collapse things, etc
# TODO: explicit "normalize airplay set" function. collapse things, etc


# TODO: airplay force setup 'selected' and/or 'volume'

# TODO: scene spec json. 
# TODO: fix mapping inp[uts/outputs not hanlding weird inputs

# TODO: homepod stereo group

# TODO: toggle on button press of remote.
# TODO: think of scenes which I actually use.

# TODO: set only inputs OR only outputs
    # - set output fails when input is not "expected"

# TODO: put wiim mappings in the controller into data

# TODO: make set/ string support muting and volume.
# TODO: scenes should have json spec
# TODO: scenes should support volumes ??
# TODO: support more streaming to specific airplay devices.
# TODO: play specific media


# INPUTS:
# - line in
# - optical in
# - airplay in
# OUTPUTS:
# - line out
# - airplay out



class SceneSpec:
    def __init__(self, curr_state, dest_state):
        self.curr_state = curr_state
        self.dest_state = dest_state

    def is_scene_valid(self):
        return None

    def get_input_change_commands(self, input_mode):
        if input_mode == "line-in":
            return ["set_line_in"]
        if input_mode == "optical":
            return ["set_optical_in"]
        return []

    def get_full_change_commands(self, input_mode, output_mode):
        commands = []

        if output_mode == "line-out":
            # line out resets input to a "default". For playback we want to sleep a sec and reset the input
            input_commands = self.get_input_change_commands(input_mode)
            commands.append("media_pause")
            commands.append("set_line_out")
            if len(input_commands) > 0:
                commands.append({"cmd": "sleep", "args": [1]})
                commands += input_commands
            commands.append("media_play")
            return commands

        elif output_mode == "airplay":
            # Always process airplay changes
            if "airplay" in self.curr_state["output"] and "airplay" in self.dest_state["output"]:
                commands += self.process_airplay_changes(self.curr_state["output"]["airplay"], self.dest_state["output"]["airplay"])
            else:
                commands += [
                    "set_airplay_out",
                ]

        elif output_mode == "coax-out":
            commands += ["set_coax_out"]

        if output_mode != "line_out":
            commands += self.get_input_change_commands(input_mode)

        return commands

    def get_output_change_commands(self, input_mode, output_mode):
        commands = []

        if output_mode == "line-out":
            # line out resets input to a "default". For playback we want to sleep a sec and reset the input
            input_commands = self.get_input_change_commands(input_mode)
            commands.append("media_pause")
            commands.append("set_line_out")
            if len(input_commands) > 0:
                commands.append({"cmd": "sleep", "args": [1]})
                commands += input_commands
            commands.append("media_play")
            return commands

        if output_mode == "airplay":
            # Always process airplay changes
            if "airplay" in self.curr_state["output"] and "airplay" in self.dest_state["output"]:
                commands += self.process_airplay_changes(self.curr_state["output"]["airplay"], self.dest_state["output"]["airplay"])
            else:
                commands += [
                    "set_airplay_out",
                ]

        if output_mode == "coax-out":
            commands += ["set_coax_out"]

        return commands



    def process_airplay_changes(self, curr_airplay_devices, dest_airplay_devices):
        commands = []

        curr_airplay_dict = dict(zip(map(lambda s: s["id"], curr_airplay_devices), curr_airplay_devices))
        dest_airplay_dict = dict(zip(map(lambda s: s["id"], dest_airplay_devices), dest_airplay_devices))

        # TODO: set airplay devices
        for airplay_id in curr_airplay_dict: 
            curr_airplay_device = curr_airplay_dict[airplay_id]
            dest_airplay_device = dest_airplay_dict[airplay_id]

            # apply selected
            if curr_airplay_device["selected"] != dest_airplay_device["selected"] and dest_airplay_device["selected"]:
                commands.append({"cmd": "enable_wireless_speaker", "args": (curr_airplay_device["id"]), "meta": curr_airplay_device["name"] })

            elif curr_airplay_device["selected"] != dest_airplay_device["selected"] and not dest_airplay_device["selected"]:
                commands.append({"cmd": "disable_wireless_speaker", "args": (curr_airplay_device["id"]), "meta": curr_airplay_device["name"] })

            # apply volume
            if curr_airplay_device["volume"] != dest_airplay_device["volume"] and dest_airplay_device["selected"]:
                commands.append({"cmd": "set_wireless_speaker_volume", "args": (curr_airplay_device["id"], dest_airplay_device["volume"]), "meta": curr_airplay_device["name"] })

        return commands

    def get_commands(self):
        output_mode = self.dest_state["output"]["mode"]
        input_mode = self.dest_state["input"]["mode"]

        input_change = input_mode != self.curr_state["input"]["mode"]
        output_change = output_mode != self.curr_state["output"]["mode"]
        airplay_mode = output_mode == "airplay"

        commands = []

        if not input_change and not output_change and not airplay_mode:
            return []

        if output_change and input_change:
            commands += self.get_full_change_commands(input_mode, output_mode)

        elif output_change:
            # cont. playback
            commands += self.get_output_change_commands(input_mode, output_mode)

        elif input_change:
            commands += self.get_input_change_commands(input_mode)

        return commands

