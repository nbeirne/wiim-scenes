#!/usr/bin/env python3

import wiim_controller
import wiim_scenes

from flask import Flask
from flask import request

app = Flask(__name__)

# ROUTES:
# set/
#   input/{input}
#   output/{output}
#
# command/<command>
# media/play
# media/pause
# media/mute/on
# mute/off
# mute/toggle
# volume/up
# volume/down
# volume/<int>


controller = wiim_controller.WiimController("192.168.2.13")

# backwards compatibility with the Wiim API
@app.route('/httpapi.asp')
def command_compat():
    command = request.args.get("command", "")
    if command is None:
        return "no command specified", 404

    return controller.run_command(command)

@app.route("/media/play")
def media_play():
    controller.media_play()
    return "OK"

@app.route("/media/pause")
def media_pause():
    controller.media_pause()
    return "OK"

@app.route("/media/toggle")
def media_toggle():
    controller.media_toggle()
    return "OK"


@app.route("/vol/up")
def volume_up():
    controller.volume_up(6)
    return "OK"

@app.route("/vol/down")
def volume_down():
    controller.volume_down(6)
    return "OK"

@app.route("/vol/<int:volume>")
def volume_set(volume):
    controller.set_volume(volume)
    return "OK"

@app.route("/mute/on")
def media_mute():
    controller.mute()
    return "OK"

@app.route("/mute/off")
def media_unmute():
    controller.unmute()
    return "OK"

@app.route("/mute/toggle")
def media_mute_toggle():
    controller.toggle_mute()
    return "OK"

@app.route("/command/<path:command>")
def run_command(command):
    return controller.run_command(command)

@app.route("/output/toggle/<out1>/<out2>")
def output_toggle(out1, out2):
    return "OK"

@app.route('/set/<path:specifier>')
def set_specifier(specifier):
    specifiers = specifier.split("/")
    if len(specifiers) > 0 and len(specifiers) % 2 == 1:
        return "invalid specifier", 400

    specifiers = list(zip(specifiers[::2], specifiers[1::2])) # pair elements

    wiim_output = None
    wiim_input = None

    for (cmd, dest) in specifiers:
        if cmd == "input":
            wiim_input = dest
        elif cmd == "output":
            wiim_output = dest
        else:
            return "unknown specifier command {0}".format(cmd), 400

    scene = wiim_scenes.SceneAnySwitch(controller, wiim_input, wiim_output)
    validated = scene.is_scene_valid()
    if validated is not None:
        print("invalid scene...")
        return validated, 400

    print("wiim_input: {0}".format(wiim_input))
    print("wiim_output: {0}".format(wiim_output))

    scene.set_scene()

    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
