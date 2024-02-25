#!/usr/bin/env python3

class WiimStateSwitchCommandGenerator:
    def __init__(self, curr_state, dest_state):
        self.curr_state = curr_state.state
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

        for airplay_id in curr_airplay_dict: 
            curr_airplay_device = curr_airplay_dict[airplay_id]
            dest_airplay_device = dest_airplay_dict[airplay_id]

            forced = "force" in dest_airplay_device and dest_airplay_device["force"]

            if not dest_airplay_device["selected"]:
                if forced or curr_airplay_device["selected"] != dest_airplay_device["selected"]:
                    commands.append({"cmd": "disable_wireless_speaker", "args": curr_airplay_device["id"], "meta": curr_airplay_device["name"] })

            # apply selected
            elif dest_airplay_device["selected"]:
                if forced or curr_airplay_device["selected"] != dest_airplay_device["selected"]:
                    commands.append({"cmd": "enable_wireless_speaker", "args": curr_airplay_device["id"], "meta": curr_airplay_device["name"] })

                # apply volume only if selected
                if forced or curr_airplay_device["volume"] != dest_airplay_device["volume"]:
                    commands.append({"cmd": "set_wireless_speaker_volume", "args": [curr_airplay_device["id"], dest_airplay_device["volume"]], "meta": curr_airplay_device["name"] })

        return commands


    def get_commands(self):
        output_mode = self.dest_state["output"]["mode"]
        input_mode = self.dest_state["input"]["mode"]
        input_change = input_mode != self.curr_state["input"]["mode"]
        output_change = output_mode != self.curr_state["output"]["mode"]
        volume_change = self.curr_state["volume"] != self.dest_state["volume"]

        airplay_mode = output_mode == "airplay"

        commands = []
        require_pause = False

        if volume_change:
            print("V")
            commands += [{ "cmd": "set_volume", "args": self.dest_state["volume"] }]

        if not input_change and not output_change and not airplay_mode:
            return commands


        input_commands = self.get_input_change_commands(input_mode)

        if output_change and output_mode == "line-out":
            require_pause = True
            # this is pretty complex.... 
            # Setting line out resets the input. But we set the input later
            # So we need to set line out, sleep a sec, and set eh input.
            # This log is self contined to line-out. 
            commands.append("set_line_out")
            if len(input_commands) > 0:
                commands += [{"cmd": "sleep", "args": [1]}]
                if not input_change:
                    commands += input_commands

        elif output_mode == "airplay":
            require_pause = True
            # Always process airplay changes
            if "airplay" in self.curr_state["output"] and "airplay" in self.dest_state["output"]:
                commands += self.process_airplay_changes(self.curr_state["output"]["airplay"], self.dest_state["output"]["airplay"])
            else:
                # this is mostly used in tests to make sure airplay commands will be filled
                # Its also a sane default if data is not formatted well.
                commands += [
                    "set_airplay_out",
                ]

        elif output_change and output_mode == "coax-out":
            commands += ["set_coax_out"]

        if input_change:
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
    def get_wiim_ip():
        if not "WIIM_IP_ADDR" in os.environ:
            return None
        wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
        return wiim_ip_addr

    wiim_device = WiimDevice(get_wiim_ip(), false)

    for line in fileinput.input():
        cmdrun = command_runer.CommandRunner(wiim_device, [line])
        cmdrun.run()

