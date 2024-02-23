import unittest

from .. import wiim_scene
from .. import wiim_cmd_gen

class TestModule(unittest.TestCase):

  def get_commands(self, curr_in, curr_out, dest_in, dest_out):
      curr_state = self.create_state(curr_in, curr_out)
      dest_scene = self.create_scene(dest_in, dest_out)
      dest_state = wiim_scene.apply_scene_over_state(curr_state, dest_scene)
      spec_scene = wiim_cmd_gen.SceneSpec(curr_state, dest_state)
      spec_scene_c = spec_scene.get_commands()
      return spec_scene_c

  def create_scene(self, dest_in, dest_out):
      json_scene = {}
      if dest_in is not None:
          json_scene["input"] = dest_in
      if dest_out is not None:
          json_scene["output"] = dest_out
      return wiim_scene.normalize_scene(json_scene)

  def create_state(self, curr_in, curr_out):
      return {"input": { "mode": curr_in }, "output": { "mode": curr_out }}

  def create_ap_state(self, curr_in, curr_out, selected_list):
      apd = []
      for idx,sel in enumerate(selected_list):
        apd.append({ "id": str(idx), "name": "n0", "type": "t", "device": "d", "selected": sel,  "volume": 50 })

      curr_state = {
        "input": { "mode": curr_in },
        "output": {
          "mode": curr_out,
          "airplay": apd,
        },
      }
      return curr_state


  def run_test(self, curr_in, curr_out, dest_in, dest_out, expected):
      curr_state = {"input": { "mode": curr_in }, "output": { "mode": curr_out }}
      json_scene = {}

      if dest_in is not None:
          json_scene["input"] = dest_in
      if dest_out is not None:
          json_scene["output"] = dest_out

      dest_scene = wiim_scene.normalize_scene(json_scene)
      dest_state = wiim_scene.apply_scene_over_state(curr_state, dest_scene)

      spec_scene = wiim_cmd_gen.SceneSpec(curr_state, dest_state)
      spec_scene_c = spec_scene.get_commands()

      msg = "Failed with {0} {1} {2} {3}".format(curr_in, curr_out, dest_in, dest_out)
      self.assertEqual(expected, spec_scene_c, msg=msg)

  def test_no_changes(self):
    self.run_test('line-in', 'airplay',  'line-in', 'airplay',  ['set_airplay_out'])
    self.run_test('line-in', 'line-out', 'line-in', 'line-out', [])
    self.run_test('optical', 'line-out', 'optical', 'line-out', [])
    self.run_test('optical', 'airplay',  'optical', 'airplay',  ['set_airplay_out'])

  def test_no_ios_specified_has_no_change(self):
    self.run_test('line-in', 'line-out', None, None, [])
    self.run_test('line-in', 'airplay',  None, None, ['set_airplay_out'])
    self.run_test('optical', 'line-out', None, None, [])
    self.run_test('optical', 'airplay',  None, None, ['set_airplay_out'])
    self.run_test('airplay', 'line-out', None, None, [])
    self.run_test('airplay', 'airplay',  None, None, ['set_airplay_out'])


  def test_none_output_is_no_change(self):
    self.run_test('line-in', 'line-out', 'line-in', None, [])
    self.run_test('line-in', 'airplay',  'line-in', None, ['set_airplay_out' ])
    self.run_test('optical', 'line-out', 'optical', None, [])
    self.run_test('optical', 'airplay',  'optical', None, ['set_airplay_out' ])


  def test_none_input_is_no_change(self):
    self.run_test('line-in', 'line-out', None, 'line-out', [])
    self.run_test('line-in', 'airplay',  None, 'airplay',  ['set_airplay_out'])
    self.run_test('optical', 'line-out', None, 'line-out', [])
    self.run_test('optical', 'airplay',  None, 'airplay',  ['set_airplay_out'])
    self.run_test('airplay', 'line-out', None, 'line-out', [])
    self.run_test('airplay', 'airplay',  None, 'airplay',  ['set_airplay_out'])

  def test_simple_input_change(self):
    self.run_test('optical', 'line-out', 'line-in', 'line-out', ['set_line_in'])
    self.run_test('airplay', 'line-out', 'line-in', 'line-out', ['set_line_in'])
    self.run_test('optical', 'airplay',  'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('airplay', 'airplay',  'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('line-in', 'line-out', 'optical', 'line-out', ['set_optical_in'])
    self.run_test('airplay', 'line-out', 'optical', 'line-out', ['set_optical_in'])
    self.run_test('line-in', 'airplay',  'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])
    self.run_test('airplay', 'airplay',  'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])

    self.run_test('optical', 'line-out', 'line-in',  None,      ['set_line_in'])
    self.run_test('optical', 'airplay',  'line-in',  None,      ['set_airplay_out', 'set_line_in'])
    self.run_test('airplay', 'line-out', 'line-in',  None,      ['set_line_in'])
    self.run_test('airplay', 'airplay',  'line-in',  None,      ['set_airplay_out', 'set_line_in'])
    self.run_test('line-in', 'line-out', 'optical',  None,      ['set_optical_in'])
    self.run_test('line-in', 'airplay',  'optical',  None,      ['set_airplay_out', 'set_optical_in'])
    self.run_test('airplay', 'line-out', 'optical',  None,      ['set_optical_in'])
    self.run_test('airplay', 'airplay',  'optical',  None,      ['set_airplay_out', 'set_optical_in'])


  def test_input_output_change(self):
    self.run_test('line-in', 'line-out', 'optical', 'coax-out', ['set_coax_out', 'set_optical_in'])
    self.run_test('optical', 'line-out', 'line-in', 'coax-out', ['set_coax_out', 'set_line_in'])
    self.run_test('airplay', 'line-out', 'line-in', 'coax-out', ['set_coax_out', 'set_line_in'])
    self.run_test('airplay', 'line-out', 'optical', 'coax-out', ['set_coax_out', 'set_optical_in'])

    self.run_test('line-in', 'line-out', 'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])
    self.run_test('optical', 'line-out', 'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('airplay', 'line-out', 'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('airplay', 'line-out', 'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])


  def test_set_only_output(self):
    self.run_test('line-in', 'line-out', 'line-in', 'coax-out', ['set_coax_out'])
    self.run_test('optical', 'line-out', 'optical', 'coax-out', ['set_coax_out'])
    self.run_test('line-in', 'line-out',  None,     'coax-out', ['set_coax_out'])
    self.run_test('optical', 'line-out',  None,     'coax-out', ['set_coax_out'])
    self.run_test('airplay', 'line-out',  None,     'coax-out', ['set_coax_out'])

    self.run_test('line-in', 'line-out', 'line-in', 'airplay',  ['set_airplay_out'])
    self.run_test('optical', 'line-out', 'optical', 'airplay',  ['set_airplay_out'])
    self.run_test('line-in', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('optical', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('airplay', 'line-out',  None,     'airplay',  ['set_airplay_out'])

  def test_unknown_inputs_does_change_output(self):
    self.run_test('0', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('0', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('0', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('0', 'line-out',  None,     'airplay',  ['set_airplay_out'])
    self.run_test('0', 'line-out', 'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])
    self.run_test('0', 'line-out', 'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('0', 'line-out', 'line-in', 'airplay',  ['set_airplay_out', 'set_line_in'])
    self.run_test('0', 'line-out', 'optical', 'airplay',  ['set_airplay_out', 'set_optical_in'])


  def test_airplay_should_enable_device(self):
    curr_state = self.create_ap_state("optical", "line-out", [False])
    dest_scene = self.create_scene("optical", { "mode": "airplay", "airplay": { "selected": True }})

    dest_state = wiim_scene.apply_scene_over_state(curr_state, dest_scene)
    spec_scene = wiim_cmd_gen.SceneSpec(curr_state, dest_state)
    spec_scene_c = spec_scene.get_commands()

    self.assertEqual([{"cmd": "enable_wireless_speaker", "args": "0", "meta": "n0" }], spec_scene_c)

  def test_reset_airplay_should_enable_device(self):
    curr_state = self.create_ap_state("optical", "airplay", [False])
    dest_scene = self.create_scene("optical", { "mode": "airplay", "airplay": { "selected": True }})

    dest_state = wiim_scene.apply_scene_over_state(curr_state, dest_scene)
    spec_scene = wiim_cmd_gen.SceneSpec(curr_state, dest_state)
    spec_scene_c = spec_scene.get_commands()

    self.assertEqual([{"cmd": "enable_wireless_speaker", "args": "0", "meta": "n0" }], spec_scene_c)


  # TODO: test airplay resolution and change
  # TODO: test volume

  def test_setting_line_out_does_do_pause_trick(self):
    self.run_test(
      'line-in', 'airplay', 'line-in', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_line_in', 'media_play'],
    )

    self.run_test(
      'line-in', 'airplay', 'optical', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_optical_in', 'media_play'],
    )

    self.run_test(
      'line-in', 'airplay', None, 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_line_in', 'media_play'],
    )

    self.run_test(
      'optical', 'airplay', 'line-in', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_line_in', 'media_play'],
    )

    self.run_test(
      'optical', 'airplay', 'optical', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_optical_in', 'media_play'],
    )

    self.run_test(
      'optical', 'airplay', None, 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_optical_in', 'media_play'],
    )

    self.run_test(
      'airplay', 'airplay', 'line-in', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_line_in', 'media_play'],
    )

    self.run_test(
      'airplay', 'airplay', 'optical', 'line-out',
      ['media_pause', 'set_line_out', {'cmd': 'sleep', 'args': [1]}, 'set_optical_in', 'media_play'],
    )

    self.run_test(
      'airplay', 'airplay', None, 'line-out',
      ['media_pause', 'set_line_out', 'media_play'],
    )





