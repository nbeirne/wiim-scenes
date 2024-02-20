#!/usr/bin/env python3

import time

import wiim_controller

# TODO: toggle on button press of remote.
# TODO: think of scenes which I actually use.

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

class SceneAnySwitch:
    def __init__(self, controller, input_mode, output_mode):
        self.controller = controller
        self.input_mode = input_mode
        self.output_mode = output_mode
        self.mapping = {

            # generalization: no changes
            #  current in  current out   desired in  desired out         result
             ("line-in",  "line-out",   "line-in",  "line-out"):        [],
             ("line-in",  "airplay",    "line-in",  "airplay"):         [],
             ("optical",  "line-out",   "optical",  "line-out"):        [],
             ("optical",  "airplay",    "optical",  "airplay"):         [],
             ("airplay",  "line-out",   "airplay",  "line-out"):        ["set_airplay_out"], # we want to reset airplay
             ("airplay",  "airplay",    "airplay",  "airplay"):         ["set_airplay_out"], # we want to reset airplay

            # generalization: changing inputs only.
            #  current in  current out   desired in  desired out         result
             ("line-in",  "line-out",   "optical",  "line-out"):        ["set_optical_in"],
             ("airplay",  "line-out",   "optical",  "line-out"):        ["set_optical_in"],
             ("line-in",  "airplay",    "optical",  "airplay"):         ["set_optical_in"],
             ("airplay",  "airplay",    "optical",  "airplay"):         ["set_optical_in"],

             ("optical",  "line-out",   "line-in",  "line-out"):        ["set_line_in"],
             ("airplay",  "line-out",   "line-in",  "line-out"):        ["set_line_in"],
             ("optical",  "airplay",    "line-in",  "airplay"):         ["set_line_in"],
             ("airplay",  "airplay",    "line-in",  "airplay"):         ["set_line_in"],


            # Support continuous playing when switching outputs. Here there be dragons.
            #  current in  current out   desired in  desired out         result
             ("line-in",  "airplay",    "line-in",  "line-out"):        ["media_pause", "set_line_out", "sleep", "set_line_in", "media_play"],
             ("line-in",  "line-out",   "line-in",  "airplay"):         ["media_pause", "set_airplay_out", "media_play"],
             ("optical",  "airplay",    "optical",  "line-out"):        ["media_pause", "set_line_out", "sleep", "set_optical_in", "media_play"],
             ("optical",  "line-out",   "optical",  "airplay"):         ["media_pause", "set_airplay_out", "media_play"],

            # Support continuous airplay streaming while changing outputs. This is tricky.
            #  current in  current out   desired in  desired out         result
             ("airplay",  "line-out",   "airplay",  "airplay"):         ["set_airplay_out"], 
             ("airplay",  "airplay",    "airplay",  "line-out"):        ["set_line_out"], # BUG: setting line out disconnects airplay...

            # if nothing else matches, these are the 'defaults' for setting up a scene.
            ("line-in", "line-out"): ["set_line_out", "sleep", "set_line_in"],
            ("optical", "line-out"): ["set_line_out", "sleep", "set_optical_in"],
            ("line-in", "airplay"):  ["set_airplay_out", "set_line_in"],
            ("optical", "airplay"):  ["set_airplay_out", "set_optical_in"],

            ("airplay", "line-out"): ["set_line_out"], # this just gets ready for airplay input. Resets to 'wifi' mode automatically
            ("airplay", "airplay"):  ["set_wifi_in", "set_airplay_out"], # setting airplay does not reset input, so set input first.
        }

    def valid_inputs(self):
        return set(map(lambda k: k[2] if len(k) >=4 else k[1], self.mapping.keys()))


    def valid_outputs(self):
        return set(map(lambda k: k[3] if len(k) >=4 else k[0], self.mapping.keys()))


    def is_scene_valid(self):
        input_valid = self.input_mode in self.valid_inputs() or self.input_mode is None 
        output_valid = self.output_mode in self.valid_outputs() or self.output_mode is None
        if input_valid and output_valid:
            return None

        msg = []
        if not input_valid:
            msg.append("invalid input {0}. use one of {1}".format(self.input_mode, self.valid_inputs()))

        if not output_valid:
            msg.append("invalid output {0}. use one of {1}".format(self.output_mode, self.valid_outputs()))

        return "\n".join(msg)


    def is_scene_set(self):
        input_mode = self.controller.get_input_mode()
        output_mode = self.controller.get_output_mode()
        return input_mode == self.input_mode and output_mode == self.output_mode

    def set_scene(self):
        current_input_mode = self.controller.get_input_mode()
        current_output_mode = self.controller.get_output_mode()

        input_mode = self.input_mode
        output_mode = self.output_mode

        if self.input_mode is None:
            input_mode = current_input_mode
        if self.output_mode is None:
            output_mode = current_output_mode

        print(current_input_mode)
        print(current_output_mode)

        key = (current_input_mode, current_output_mode, input_mode, output_mode)
        print(key)
        if not key in self.mapping:
            print("no shortcut: {0}/{1} -> {2}/{3}".format(key[0], key[1], key[2], key[3]))

            key = (input_mode, output_mode)
            if not key in self.mapping:
                print("unsupported path: {0}/{1}".format(key[0], key[1]))
                return

        commands = self.mapping[key]
        print("commands: %s" % commands)
        for command in commands:
            if command == "sleep":
                time.sleep(1)

            else:
                func = getattr(self.controller, command)
                if func != None:
                    func()
                else:
                    print("unknown command: %s" % command)

if __name__ == '__main__':
    controller = wiim_controller.WiimController("192.168.2.13")
    controller.setStreamToAllAirplay()

