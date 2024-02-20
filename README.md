# Wiim Scene

This is proxy server meant to sit between any of your exising Home automation and a Wiim device. 

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
This API is backwards compatible with the Wiim API. There is also a more convenient endpoint which is equivilant.

```
curl http://$ip:$port/httpapi.asp?command=$command
curl http://$ip:$port/command/$command
```
