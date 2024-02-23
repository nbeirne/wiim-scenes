#!/usr/bin/env python3

from ..util import command_runner

# TODO: only pause if media is playing OR changing outputs AND playing audio

# TODO: fix flask scenes
# TODO: feature: global volume control in scene

# TODO refactor: auto normalize scenes, commands, and states

# TODO feature: airplay device query: seperate  "query" and "set"
# TODO feature: play specific media
# TODO feature: homepod stereo groups


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


    def process_airplay_changes(self, curr_airplay_devices, dest_airplay_devices):
        commands = []

        curr_airplay_dict = dict(zip(map(lambda s: s["id"], curr_airplay_devices), curr_airplay_devices))
        dest_airplay_dict = dict(zip(map(lambda s: s["id"], dest_airplay_devices), dest_airplay_devices))

        # TODO: set airplay devices
        for airplay_id in curr_airplay_dict: 
            curr_airplay_device = curr_airplay_dict[airplay_id]
            dest_airplay_device = dest_airplay_dict[airplay_id]

            forced = "force" in dest_airplay_device and dest_airplay_device["force"]

            if (forced or curr_airplay_device["selected"] != dest_airplay_device["selected"]) and not dest_airplay_device["selected"]:
                commands.append({"cmd": "disable_wireless_speaker", "args": curr_airplay_device["id"], "meta": curr_airplay_device["name"] })

            # apply selected
            elif (forced or curr_airplay_device["selected"] != dest_airplay_device["selected"]) and dest_airplay_device["selected"]:
                commands.append({"cmd": "enable_wireless_speaker", "args": curr_airplay_device["id"], "meta": curr_airplay_device["name"] })

                # apply volume only if selected
                if (forced or curr_airplay_device["volume"] != dest_airplay_device["volume"]) and dest_airplay_device["selected"]:
                    commands.append({"cmd": "set_wireless_speaker_volume", "args": [curr_airplay_device["id"], dest_airplay_device["volume"]], "meta": curr_airplay_device["name"] })

        return commands


    def get_commands(self):
        output_mode = self.dest_state["output"]["mode"]
        input_mode = self.dest_state["input"]["mode"]
        input_change = input_mode != self.curr_state["input"]["mode"]
        output_change = output_mode != self.curr_state["output"]["mode"]

        airplay_mode = output_mode == "airplay"

        if not input_change and not output_change and not airplay_mode:
            return []

        require_pause = False
        commands = []

        input_commands = self.get_input_change_commands(input_mode)

        if output_change and output_mode == "line-out":
            require_pause = True
            # line out resets input to a "default". For playback we want to sleep a sec and reset the input
            commands.append("set_line_out")
            if len(input_commands) > 0:
                commands.append({"cmd": "sleep", "args": [1]})

        elif output_mode == "airplay":
            # Always process airplay changes
            if "airplay" in self.curr_state["output"] and "airplay" in self.dest_state["output"]:
                commands += self.process_airplay_changes(self.curr_state["output"]["airplay"], self.dest_state["output"]["airplay"])
            else:
                commands += [
                    "set_airplay_out",
                ]

        elif output_change and output_mode == "coax-out":
            commands += ["set_coax_out"]

        if input_change or output_mode == "line-out":
            commands += input_commands


        if require_pause:
            commands = [
                "media_pause",
                *commands,
                "media_play",
            ]

        return commands

if __name__ == "__main__":
    import fileinput
    import util.command_runner
    def get_wiim_ip():
        if not "WIIM_IP_ADDR" in os.environ:
            return None
        wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
        return wiim_ip_addr

    controller = wiim_controller.WiimController(get_wiim_ip(), false)

    for line in fileinput.input():
        cmdrun = command_runer.CommandRunner(controller, [line])
        cmdrun.run()

