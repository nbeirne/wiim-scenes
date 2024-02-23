import os
import sys
import json
import argparse

import util.command_runner as command_runner

import wiim_controller
import wiim_cmd_gen
import wiim_state
import wiim_scene


parser = argparse.ArgumentParser(
    prog='set_scene.py',
    description='Set wiim scenes.',
    #epilog='Epilog'
)
parser.add_argument('-f', '--filename', action='append', nargs='?')
parser.add_argument('-s', '--scene', action='append', nargs='?')


def get_wiim_ip():
    if not "WIIM_IP_ADDR" in os.environ:
        return None
    wiim_ip_addr = os.environ["WIIM_IP_ADDR"]
    return wiim_ip_addr

def get_current_state(fetch_airplay=False):
    player_status = controller.get_player_status()
    player_output_state = controller.get_output_state()
    player_airplay_speakers = None
    if wiim_controller.parse_output_state(player_output_state) == "airplay" or fetch_airplay:
        player_airplay_speakers = controller.get_airplay_speakers()
    return wiim_state.parse_current_state(player_status, player_output_state, player_airplay_speakers)

def set_scene(json_scene):
    # validate
    scene = wiim_scene.normalize_scene(json_scene)

    # grab wiim info
    player_status = controller.get_player_status()
    player_output_state = controller.get_output_state()
    player_airplay_speakers = None
    if wiim_controller.parse_output_state(player_output_state) == "airplay" or ("output" in scene and scene["output"]["mode"] == "airplay"):
        player_airplay_speakers = controller.get_airplay_speakers()

    # get commands to run
    current_state = wiim_state.parse_current_state(player_status, player_output_state, player_airplay_speakers)
    new_state = wiim_scene.apply_scene_over_state(current_state, scene)
    commands = wiim_cmd_gen.SceneSpec(current_state, new_state).get_commands()

    print("commands: {0}".format(json.dumps(commands,indent=2)))

    # run them
    runner = command_runner.CommandRunner(controller, commands)
    runner.run()


if __name__ == "__main__":
    controller = wiim_controller.WiimController(get_wiim_ip())

    args = vars(parser.parse_args())
    print(args)

    scenes = list(map(json.loads, args["scene"])) if args["scene"] is not None else []

    if args["filename"] is not None:
        for fn in args["filename"]:
            with open(fn) as file:
                json_scene = json.load(file)
                scenes.append(json_scene)

    if len(scenes) > 0:
        # find matching
        print(scenes)
        scenes = list(map(wiim_scene.normalize_scene, scenes))
        print(scenes)

        fetch_airplay = any(map(lambda s: "output" in s and s["output"]["mode"] == "airplay", scenes))
        current_state = get_current_state(fetch_airplay)
        dest_scene = scenes[0]
        for idx,scene in enumerate(scenes):
            if wiim_scene.does_state_match_scene(current_state, scene):
                dest_scene = scenes[(idx + 1) % len(scenes)]

        set_scene(dest_scene)
    else:
        print("No scenes provided")

