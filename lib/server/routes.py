#!/usr/bin/env python3

import os

from flask import Flask
from flask import request

from ..util import command_runner

from ..wiim_scene import wiim_controller 
from ..wiim_scene import wiim_cmd_gen
from ..wiim_scene import wiim_state
from ..wiim_scene import wiim_scene

def get_wiim_ip():
    if not "WIIM_IP_ADDR" in os.environ:
        return None
    wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
    return wiim_ip_addr


wiim_ip_addr = get_wiim_ip()
if wiim_ip_addr is None:
    print("You must set WIIM_IP_ADDR in the environment")
    exit(1)

controller = wiim_controller.WiimController(wiim_ip_addr)
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


def run_scene(controller, scene):
    cr = command_runner.SceneRunner(controller, scene)
    validated = cr.is_scene_valid()

    if validated is not None:
        return validated, 400

    cr.set_scene()

    return "OK"


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


# Below here are the interesting commands


@app.route('/scene/current')
def current_scene():
    player_status = controller.get_player_status()
    player_output_state = controller.get_output_state()
    player_airplay_speakers = None
    if wiim_controller.parse_output_state(player_output_state) == "airplay":
        player_airplay_speakers = controller.get_airplay_speakers()

    return wiim_state.parse_current_state(player_status, player_output_state, player_airplay_speakers)

@app.route("/output/toggle/<path:outputs_str>")
def output_toggle(outputs_str):
    outputs = outputs_str.split("/")
    if len(outputs) <= 0:
        return "No outputs specified", 400

    current_input_mode = controller.get_input_mode()
    current_output_mode = controller.get_output_mode()
    current_idx = outputs.index(current_output_mode)
    if current_idx is None:
        current_idx = 0

    next_idx = (current_idx + 1) % len(outputs)
    wiim_output = outputs[next_idx]

    spec = {
        "output": wiim_output
    }
    scene = wiim_cmd_gen.SceneSpec(current_input_mode, current_output_mode, None, spec)
    return run_scene(controller, scene)


@app.route('/set/<path:specifier>')
def set_specifier(specifier):
    specifiers = specifier.split("/")
    if len(specifiers) > 0 and len(specifiers) % 2 == 1:
        return "invalid specifier", 400

    specifiers = list(zip(specifiers[::2], specifiers[1::2])) # pair elements

    scene = {
        "input": None,
        "output": None, 
        "airplay_devices": None, # { name: string, volume: int }
        "volume": None,
    }

    wiim_output = None
    wiim_input = None

    commands = {
        "input": 1,
        "output": 1,
    }

    for (cmd, dest) in specifiers:
        if cmd == "input":
            wiim_input = dest
        elif cmd == "output":
            wiim_output = dest
        else:
            return "unknown specifier command {0}".format(cmd), 400

    current_input_mode = controller.get_input_mode()
    current_output_mode = controller.get_output_mode()

    spec = {
        "input": wiim_input,
        "output": wiim_output,
    }
    scene = wiim_cmd_gen.SceneSpec(current_input_mode, current_output_mode, None, spec)
    return run_scene(controller, scene)


@app.route("/raw/scene/<path:scene>")
def set_raw_scene(scene):
    scene = wiim_scene.SceneSpec(controller, scene)
    validated = scene.is_scene_valid()
    if validated is not None:
        print("invalid scene...")
        return validated, 400
    scene.set_scene()
    return "OK"

