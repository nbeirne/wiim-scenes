#!/usr/bin/env python3

import requests
import json
import urllib3

urllib3.disable_warnings()


def parse_input_mode(mode):
    if mode == "1": # mode 1 is actually airplay
        return "airplay"
    if mode == "10": 
        return "default"
    if mode == "31":
        return "spotify"
    if mode == "40":
        return "line-in"
    if mode == "43":
        return "optical"
    return mode

def parse_output_state(state):
    if state["source"] == "1":
        return "bluetooth"
    if state["airplay"] == "1":
        return "airplay"
    if state["hardware"] == "1":
        return "optical"
    if state["hardware"] == "2":
        return "line-out"
    if state["hardware"] == "3":
        return "coax-out"
    return state


class WiimController:
    # https://www.wiimhome.com/pdf/HTTP%20API%20for%20WiiM%20Mini.pdf
    def __init__(self, ip, verbose=0):
        self.ip = ip
        self.verbose = verbose

    def run_command(self, command):
        url = "https://%s/httpapi.asp?command=%s" % (self.ip, command)
        response = requests.get(url, verify=False)
        if self.verbose == 1:
            print("API command: {0}".format(command))
        if self.verbose == 2:
            print("API command: {0}, got {1}".format(command, response.text))
        return response.text

    def get_player_status(self):
        text = self.run_command("getPlayerStatus")
        data = json.loads(text)
        return data

    # Input settings

    def get_input_mode(self):
        mode = self.get_player_status()["mode"]
        return parse_input_mode(mode)

    def set_line_in(self):
        self.run_command("setPlayerCmd:switchmode:line-in")

    def set_optical_in(self):
        self.run_command("setPlayerCmd:switchmode:optical")

    def set_wifi_in(self):
        self.run_command("setPlayerCmd:switchmode:wifi")

    def media_play_url(self, url):
        self.run_command("setPlayerCmd:play:{0}".format(url))

    # playlist index https://10.10.10.254/httpapi.asp?command=setPlayerCmd:playlist:url:<index>

    # Output settings

    def get_output_state(self):
        text = self.run_command("getNewAudioOutputHardwareMode")
        return json.loads(text) 

    def get_output_mode(self):
        return parse_output_state(self.getOutputState())

    def get_airplay_speakers(self):
        text = self.run_command("audio_cast:get_speaker_list")
        data = json.loads(text)
        outputs = filter(lambda output: output["type"] == "AirPlay 2", data["outputs"])
        return list(outputs)

    def enable_wireless_speaker(self, ident):
        self.run_command("audio_cast:speaker_enable:{0}".format(ident))

    def disable_wireless_speaker(self, ident):
        self.run_command("audio_cast:speaker_disable:{0}".format(ident))

    def set_wireless_speaker_volume(self, ident, volume):
        volume = int(volume)
        volume = max(0,min(100,volume))
        self.run_command("audio_cast:speaker_set_volume:{0}:{1}".format(ident, volume))

    def set_airplay_out(self, names=None):
        speakers = self.get_airplay_speakers()
        for speaker in speakers:
            if names is None or speaker["name"] in names:
                self.enable_wireless_speaker(speaker["id"])

    def set_line_out(self):
        self.run_command("setAudioOutputHardwareMode:2")

    # Media controls

    def media_play(self):
        self.run_command("setPlayerCmd:play")

    def media_pause(self):
        self.run_command("setPlayerCmd:pause")

    def media_toggle(self):
        self.run_command("setPlayerCmd:onepause")

    # Volume up and down

    def get_volume(self, status=None):
        if status is None:
            status = self.get_player_status()
        return status["vol"]

    def set_volume(self, volume):
        volume = int(volume)
        volume = max(0,min(100,volume))
        self.run_command("setPlayerCmd:vol:{0}".format(volume))

    def volume_up(self, step):
        volume = int(self.get_volume())
        self.set_volume(volume + step)

    def volume_down(self, step):
        volume = int(self.get_volume())
        self.set_volume(volume - step)

    # Mute and toggles

    def mute(self):
        self.run_command("setPlayerCmd:mute:0")

    def unmute(self):
        self.run_command("setPlayerCmd:mute:1")

    def toggle_mute(self, status=None):
        if status is None:
            status = self.get_player_status()
        muted = status["mute"] == "0"
        if (muted):
            self.unmute()
        else:
            self.mute()

