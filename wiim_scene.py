#!/usr/bin/env python3

import os
import json
import argparse

from lib.wiim_scene.wiim_device      import WiimDevice
from lib.util.schema                 import ValidationError
from lib.wiim_scene.wiim_scene       import WiimScene
from lib.wiim_scene.scene_controller import SceneController


parser = argparse.ArgumentParser(
    prog='set_scene.py',
    description='Set wiim scenes.',
    #epilog='Epilog'
)
parser.add_argument('-c', '--current', action='store_true')
parser.add_argument('-f', '--filename', action='append', nargs='?')
parser.add_argument('-s', '--scene', action='append', nargs='?')
parser.add_argument('-d', '--dry-run', action='store_true')
parser.add_argument('-v', '--verbose', action='count', default=0)

verbose=0
dry_run=False

def get_wiim_ip():
    if not "WIIM_IP_ADDR" in os.environ:
        return None
    wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
    return wiim_ip_addr


def load_file_scenes(filenames):
    if type(filenames) is not list:
        filenames = [filenames]

    scenes = []

    for filename in filenames:
        with open(filename, "r") as f:
            json_scene = json.load(f)
            if type(json_scene) is list:
                scenes += list(map(WiimScene, json_scene))
            else:
                scenes += [WiimScene(json_scene)]

    return scenes

def load_json_scenes(input_strs):
    if type(input_strs) is not list:
        input_strs = [input_strs]

    scenes = []

    for input_str in input_strs:
        json_scene = json.loads(input_str)
        if type(json_scene) is list:
            scenes += list(map(WiimScene, json_scene))
        else:
            scenes += [WiimScene(json_scene)]

    return scenes


if __name__ == "__main__":
    args = vars(parser.parse_args())

    verbose=args["verbose"]
    dry_run=args["dry_run"]
    wiim_device = WiimDevice(get_wiim_ip(), verbose=verbose)
    scene_controller = SceneController(wiim_device)

    if args["current"] == True:
        print(json.dumps(scene_controller.get_current_scene(fetch_airplay=True).state))
        exit(0)

    try:
        scenes = []

        if args["scene"] is not None:
            scenes += load_json_scenes(args["scene"])

        if args["filename"] is not None:
            scenes += load_file_scenes(args["filename"])

        if len(scenes) > 0:
            scene_controller.set_scenes(scenes, dry_run=dry_run, verbose=verbose)
        else:
            print("No scenes provided")
    except ValidationError as e:
        print("input error: {0}".format(e))

