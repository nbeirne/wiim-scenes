import json

from ..util.command_runner import CommandRunner

from .wiim_cmd_gen import WiimStateSwitchCommandGenerator
from .             import wiim_device 
from .             import wiim_state

class SceneController:
    def __init__(self, wiim_device):
        self.wiim_device = wiim_device
        pass

    def get_current_scene(self, fetch_airplay=False):
        player_status = self.wiim_device.get_player_status()
        player_output_state = self.wiim_device.get_output_state()
        player_airplay_speakers = None
        if fetch_airplay or wiim_device.parse_output_state(player_output_state) == "airplay":
            player_airplay_speakers = self.wiim_device.get_airplay_speakers()

        return wiim_state.parse_current_state(player_status, player_output_state, player_airplay_speakers)

    def set_scenes(self, scenes, return_type=None, dry_run=False, verbose=False):
        scene = None

        fetch_airplay = any(map(lambda s: s.output_mode() == "airplay", scenes))
        current_state = self.get_current_scene(fetch_airplay)

        if len(scenes) == 1:
            scene = scenes[0]
        else:
            for idx,scene in enumerate(scenes):
                if current_state.does_scene_match(scene):
                    scene = scenes[(idx+1) % len(scenes)]
                    break

        new_state = current_state.apply_scene(scene)
        commands = WiimStateSwitchCommandGenerator(current_state, new_state).get_commands()

        if verbose:
            print("curr state: {0}".format(json.dumps(current_state, indent=2)))
            print("set scene:  {0}".format(json.dumps(scene.scene, indent=2)))
            print("dest state: {0}".format(json.dumps(new_state, indent=2)))
            print("commands:   {0}".format(json.dumps(commands, indent=2)))

        if not dry_run:
            command_runner = CommandRunner(self.wiim_device, commands)
            command_runner.run()

        if return_type == "state":
            return new_state
        elif return_type == "cmd":
            return commands
        elif return_type is not None:
            raise ValueError("debug command not found")

