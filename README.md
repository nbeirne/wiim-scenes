# Wiim Scene

***THIS MAY NOT WORK WITH YOUR WIIM IF ITS NOT A WIIM PRO***

This is proxy server meant to sit between any of your exising Home automation and a Wiim Pro. It is intended to provide higher-level functionality over the existing API. I use it with a Lutron Caseta remote and Home Assistant.


Using this has several benefits over using the Wiim api directly:
- This supports output switching.
- Support media mute toggling and volume stepping.
- The API is less obtuse.
- It uses HTTP instead of a self-signed HTTPS certificate. 


## Set Up 

There are several ways to run the server. 
- Docker (see the Makefile for an example setup)
- On your machine (also see the Makefile to install deps and running the dev environment)

Essentially:
```
> export WIIM_IP_ADDR="<ip>"
> pip install --no-cache-dir -r requirements.txt
> flask --app ./app/flask_server.py run 
```


## Usage

### Controlling Playback
```
curl http://$ip:$port/media/play
curl http://$ip:$port/media/pause
curl http://$ip:$port/media/toggle
```

### Volume and Muting
```
curl http://$ip:$port/vol/mute
curl http://$ip:$port/vol/up
curl http://$ip:$port/vol/down
curl http://$ip:$port/vol/$volume # volume is between 0 and 100
```

### Setting Scenes and Outputs
```
curl http://$ip:$port/outputs/toggle/<list>/<of>/<outputs> # Rotate through the list of outputs.
curl http://$ip:$port/set/output/$output
curl http://$ip:$port/set/input/$input
curl http://$ip:$port/set/input/$input/output/$output
```

#### Supported outputs:
```
airplay
line-out
```

#### Supported inputs:
```
line-in
optical
airplay # in some circumstances. Airplay cannot be started really.
```

### Commands
This API is backwards compatible with the Wiim API. There is also a more convenient endpoint which is equivalent.

```
curl http://$ip:$port/httpapi.asp?command=$command
curl http://$ip:$port/command/$command
```


## The Wiim API
This project is possible through the use of a few undocumented Wiim APIs. Here is a list of useful endpoints fo this project, but please be careful.

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

The documented API commands are available [here](https://www.wiimhome.com/pdf/HTTP%20API%20for%20WiiM%20Mini.pdf). There is a full list of API commands in [http-api.txt](./http-api.txt)


