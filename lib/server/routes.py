#!/usr/bin/env python3

import os
import json
import traceback

from flask import Flask
from flask import request

from ..util.schema import ValidationError

from ..wiim_scene.wiim_device      import WiimDevice
from ..wiim_scene.wiim_scene       import WiimScene
from ..wiim_scene.scene_controller import SceneController

from .scene_db import SceneDb, load_scenes_from_json


# TODO: simplify access of the internals to state/scene.
# TODO: make a Scene a subclass of state, or vice versa

# TODO: use comparison operator for checking if a scene matches a state
    # ie, run the merge then equality check it.

####

# TODO feature: airplay device query: seperate  "query" and "set"
# TODO feature: play specific media
# TODO feature: homepod stereo groups
# TODO feature: get and set EQ
# TODO feature: debug /apply and /cmd should work with named scenes


# Scene API:

# /scene             GET current scene.                                               POST with JSON to set scene. If JSON is list: find current and go to the next one.
# /scene/debug/state GET the state that this scene would go to
# /scene/debug/cmd   GET the list of commands which would be run

# /scenes             GET list of scenes.  POST with a name or a list to set the scene
# /scenes/<name>      GET to get json.     PUT with JSON to save a scene to this name. POST to set scene.


# Basic API 

# command/<command>

# media/play
# media/pause
# media/toggle

# media/mute/on
# mute/off
# mute/toggle
# volume/up
# volume/up/<int>
# volume/down
# volume/down/<int>
# volume/<int>
#


def get_wiim_ip():
    if not "WIIM_IP_ADDR" in os.environ:
        return None
    wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
    return wiim_ip_addr

def get_scene_db_path():
    if not "WIIM_SCENE_DB_PATH" in os.environ:
        return ".scenes"
    wiim_scene_db_path = os.environ["WIIM_SCENE_DB_PATH"]
    return wiim_scene_db_path

wiim_ip_addr = get_wiim_ip()
if wiim_ip_addr is None:
    print("You must set WIIM_IP_ADDR in the environment")
    exit(1)


wiim_device = WiimDevice(wiim_ip_addr, verbose=True)
app = Flask(__name__)



# backwards compatibility with the Wiim API
@app.route('/httpapi.asp')
def command_compat():
    command = request.args.get("command", "")
    if command is None:
        return "no command specified", 404

    return wiim_device.run_command(command)


@app.route("/command/<path:command>")
def run_command(command):
    return wiim_device.run_command(command)


@app.route("/media/play")
def media_play():
    wiim_device.media_play()
    return "OK"

@app.route("/media/pause")
def media_pause():
    wiim_device.media_pause()
    return "OK"

@app.route("/media/toggle")
def media_toggle():
    wiim_device.media_toggle()
    return "OK"


@app.route("/vol/up", defaults={"amount": 6})
@app.route("/vol/up/<int:amount>")
def volume_up(amount):
    wiim_device.volume_up(amount)
    return "OK"

@app.route("/vol/down", defaults={"amount": 6})
@app.route("/vol/down/<int:amount>")
def volume_down(amount):
    wiim_device.volume_down(amount)
    return "OK"

@app.route("/vol/<int:volume>")
def volume_set(volume):
    wiim_device.set_volume(volume)
    return "OK"

@app.route("/mute/on")
def media_mute():
    wiim_device.mute()
    return "OK"

@app.route("/mute/off")
def media_unmute():
    wiim_device.unmute()
    return "OK"

@app.route("/mute/toggle")
def media_mute_toggle():
    wiim_device.toggle_mute()
    return "OK"


# Below here are the interesting commands


@app.route('/scene', methods=['GET', 'POST'])
def route_scene():
    if request.method == 'GET':
        state = SceneController(wiim_device).get_current_scene()
        return json.dumps(state.state)

    else:
        json_scene = request.get_json(force=True)
        scenes = None
        try:
            scenes = load_scenes_from_json(json_scene)
        except ValidationError as e:
            return "input error: {0}".format(e), 400

        if len(scenes) == 0:
            return "provide at least one scene!", 400

        try:
            SceneController(wiim_device).set_scenes(scenes)
        except ValidationError as e:
            return "internal error: {0}".format(e), 500

        return "OK", 200


@app.route('/scene/debug/<string:return_mode>', methods=['POST'])
def debug_scene(return_mode):
    json_scene = request.get_json(force=True)
    scenes = None
    try:
        scenes = load_scenes_from_json(json_scene)
    except ValidationError as e:
        return "input error: {0}".format(e), 400

    if len(scenes) == 0:
        return "provide at least one scene!", 400

    try:
        return json.dumps(SceneController(wiim_device).set_scenes(scenes, dry_run=True, return_type=return_mode))
    except ValueError as e:
        return "input error: {0}".format(e), 400
    except Exception as e:
        return "internal error: {0}".format(e), 500



@app.route("/scenes", methods=['GET', 'POST'])
def get_scenes():
    if request.method == 'GET':
        return json.dumps(SceneDb(get_scene_db_path()).list_all())

    if request.method == 'POST':
        try: 
            db = SceneDb(get_scene_db_path())
            scene_names = request.data.decode('ascii')
            try:
                scene_names = json.loads(scene_names)
            except json.JSONDecodeError:
                pass

            scenes = db.load(scene_names)
            SceneController(wiim_device).set_scenes(scenes)

            return "OK"

        except Exception as e:
            print(traceback.format_exc())
            return str(e), 500

@app.route("/scenes/<string:name>", methods=['GET', 'POST', 'PUT'])
def named_scene(name):
    if request.method == 'GET':
        try:
            scenes = SceneDb(get_scene_db_path()).load(name)
            return json.dumps(list(map(lambda s:s.scene, scenes)))
        except Exception as e:
            return str(e), 400

    elif request.method == 'POST':
        json_scene = request.get_json(force=True)
        SceneDb(get_scene_db_path()).save_json(name, json_scene)
        return "OK"

    elif request.method == 'PUT':
        scenes = SceneDb(get_scene_db_path()).load(name)
        SceneController(wiim_device).set_scenes(scenes)
        return "OK"

@app.route("/scenes/<string:name>/debug/<string:return_mode>", methods=['GET'])
def debug_named_scene(name, return_mode):
    try:
        scenes = SceneDb(get_scene_db_path()).load(name)
        return json.dumps(SceneController(wiim_device).set_scenes(scenes, dry_run=True, return_type=return_mode))
    except ValueError as e:
        return "input error: {0}".format(e), 400
    except Exception as e:
        return "internal error: {0}".format(e), 500

