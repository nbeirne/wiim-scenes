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
parser.add_argument('-d', '--dry_run', action='store_true')
parser.add_argument('-v', '--verbose', action='count', default=0)

verbose=0
dry_run=False

def get_wiim_ip():
    if not "WIIM_IP_ADDR" in os.environ:
        return None
    wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
    return wiim_ip_addr


if __name__ == "__main__":
    args = vars(parser.parse_args())

    verbose=args["verbose"]
    dry_run=args["dry_run"]
    wiim_device = WiimDevice(get_wiim_ip(), verbose=verbose)
    scene_controller = SceneController(wiim_device)

    if args["current"] == True:
        print(json.dumps(scene_controller.get_current_scene(fetch_airplay=True)))
        exit(0)


    scenes = list(map(json.loads, args["scene"])) if args["scene"] is not None else []

    if args["filename"] is not None:
        for fn in args["filename"]:
            with open(fn) as file:
                json_scene = json.load(file)
                scenes.append(json_scene)

    if len(scenes) > 0:
        try:
            scenes = list(map(WiimScene, scenes))
            scene_controller.set_scenes(scenes, dry_run=dry_run, verbose=verbose)
        except ValidationError as e:
            print("input error: {0}".format(e))
    else:
        print("No scenes provided")

