# Wiim Scene

***THIS MAY NOT WORK WITH YOUR WIIM IF ITS NOT A WIIM PRO***

This is proxy server meant to sit between any of your exising Home automation and a Wiim Pro. It is intended to provide higher-level functionality over the existing API. I use it with a Lutron Caseta remote and Home Assistant.


Using this has several benefits over using the Wiim api directly:
- Scenes. You may set up scenes of inputs, outputs, and volumes and switch between them.
- This supports output switching.
- Support media mute toggling and volume stepping.
- The API is less obtuse.
- It uses HTTP instead of a self-signed HTTPS certificate.

## Set Up 

### CLI

There is a command line interface. Usage:
```
> export WIIM_IP_ADDR="<ip>"
> ./wiim_scene.py --current
> ./wiim_scene.py [-f <scene json file>] [-s <scene json>] [--dry-run] [--verbose]
```

### REST Server Interface

There are several ways to run the server. 
- Docker (see the Makefile for an example setup)
- On your machine (also see the Makefile to install deps and running the dev environment)

Essentially:
```
> export WIIM_IP_ADDR="<ip>"
> pip install --no-cache-dir -r requirements.txt
> flask --app ./server.py run 
```

## Scenes
A scene schema exists in lib/wiim_scene/wiim_scene.py. Any of the parameters may be omitted. There are several examples in the ./scenes directory.
```
{
    "volume": number,
    "input": {
        "mode": "line-in | optical"
    }
    "output": {
        "mode": "line-out | coax-out | airplay",
        "airplay": [
            {
                "name": "name to query",
                "id": "id to query",
                "device": "device type to query",
                "selected": boolean,
                "volume": int,
                "notes": [
                    "Query airplay devices by name, id, and device type. Sets selected and volume if present.",
                    "If selected is not present it defaults to true",
                    "When there are multiple of these lists, the last match takes priority"
                ]
            }
        ]
    }
}
```

These scenes can be annoying to write. There are shortcuts to writing them. 
1. The input mode may be specified with a simple string. Example: `{ "input": "line-in" }`.
2. The output mode may be specified with a simple string. Example: `{ "output": "line-out" }`.
3. If outputing to airplay and there is no airplay dictionary, it defaults to selecting all airplay devices.
4. An airplay device list may just use the name, instead of specifying a full dictionary. Example: `{ "output": { "mode": "airplay", "airplay": ["device1", "device2"] }`

Any place which takes a Scene as input may also take a list of scenes. If the current state matches the inputs/outputs of a scene in the list, it will rotate through to he next scene. Volume settings are ignored for now.

### Supported inputs:
```
line-in
optical
airplay # in some circumstances. Airplay cannot be started really.
```


## REST Usage

### Controlling Playback
```
curl http://$ip:$port/media/play
curl http://$ip:$port/media/pause
curl http://$ip:$port/media/toggle
```

### Volume and Muting
```
curl http://$ip:$port/vol/up
curl http://$ip:$port/vol/up/$increment
curl http://$ip:$port/vol/down
curl http://$ip:$port/vol/down/$increment
curl http://$ip:$port/vol/$volume # volume is between 0 and 100

curl http://$ip:$port/mute/on
curl http://$ip:$port/mute/off
curl http://$ip:$port/mute/toggle
```

### Setting Scenes and Outputs
```
curl http://$ip:$port/scene # GET to get the current scene. POST with a scene JSON to set a scene.
```

You may also POST a list of scenes to the scene endpoint. If a match to the current state exists in that list, it rotates to the next scene.

### Commands
This API is backwards compatible with the Wiim API. There is also a more convenient endpoint which is equivalent.

```
curl http://$ip:$port/httpapi.asp?command=$command
curl http://$ip:$port/command/$command
```

## The Wiim API
This project is possible through the use of a few undocumented Wiim APIs. Here is a list of useful endpoints for this (or similar) project, but please be careful.

```
curl http://$WIIM_IP_ADDR/httpapi.asp?command=getNewAudioOutputHardwareMode # get current output modes. hardware=1 is optical, hardware=2 is line-out, hardware=3 is coax-out.
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:get_speaker_list   # get wireless speaker list, including airplay2.
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_enable:$id # enable speaker using an id from the speaker list
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_set_password:$id:$password # unused in this project
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_set_volume:$id:$number # unused in this project
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_set_volume:$id:$number # unused in this project
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_disable:$id # unused in this project
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_stereo_group_disable:$id # unused in this project
curl http://$WIIM_IP_ADDR/httpapi.asp?command=audio_cast:speaker_stereo_group_enable:$id # unused in this project

```

The documented API commands are available [here](https://www.wiimhome.com/pdf/HTTP%20API%20for%20WiiM%20Mini.pdf). A full list of the undocumented API commands I found are in [http-api.txt](./http-api.txt)


