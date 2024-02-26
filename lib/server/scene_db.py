
import os
import json
import errno

from ..wiim_scene.wiim_scene import WiimScene

def make_sure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

def load_scenes_from_json(json_scene):
    if type(json_scene) is list:
        return list(map(WiimScene, json_scene))
    else:
        return [WiimScene(json_scene)]

class SceneDb:
    def __init__(self, scene_dir):
        self.scene_dir = scene_dir
        make_sure_path_exists(scene_dir)


    def save_json(self, name, json_scene):
        # do a quick validation before saving
        load_scenes_from_json(json_scene)
        self.save(name, json_scene)

    def save(self, name, scene):
        with open("{0}/{1}.json".format(self.scene_dir, name), "w") as f:
            scenes = None
            if type(scene) is list:
                scenes = list(map(lambda s: s, scene))
            else:
                scenes = scene.scene
            json.dump(scenes, f)

    def load(self, names):
        if type(names) is str:
            names = [names]

        scenes = []

        for name in names:
            with open("{0}/{1}.json".format(self.scene_dir, name), "r") as f:
                json_scene = json.load(f)
                if type(json_scene) is list:
                    scenes += list(map(WiimScene, json_scene))
                else:
                    scenes += [WiimScene(json_scene)]

        return scenes

    def list_all(self):
        return list(map(lambda fn: fn.removesuffix(".json"), os.listdir(self.scene_dir)))

