# mlbtv-muter

Python script which periodically checks for an active MLB.TV window, takes a screenshot of it, and OCR's to identify whether a commercial break is in progress. When a break is in progress, it mutes the system audio, and automatically unmutes after enough time has passed of the commercial break text no longer appearing in the screenshot.

## Setup
### MacOS
```bash
git clone https://github.com/jwoglom/mlbtv-muter
cd mlbtv-muter
pipenv install
pipenv run mlbtvmuter
```

## Options
```bash
usage: mlbtvmuter.py [-h] [--interval INTERVAL] [--unmute-after UNMUTE_AFTER] [--once] [--ensure-front] [--skip-not-front] [--app-name APP_NAME] [--title-keyword TITLE_KEYWORD]
                     [--audio-method AUDIO_METHOD] [--audio-device AUDIO_DEVICE] [--debug]

Automatically mute the system audio when commercials are playing on MLB.TV

options:
  -h, --help            show this help message and exit
  --interval INTERVAL   the interval in seconds in which the window status is checked
  --unmute-after UNMUTE_AFTER
                        the interval in seconds in which the system audio should be unmuted once detected that a commercial is no longer playing
  --once                when set, runs once instead of in a loop
  --ensure-front        when set, forces the MLB.TV window to the foreground
  --skip-not-front      when set, ignores checking when the MLB.TV window is not in the foreground
  --app-name APP_NAME   the MacOS application name which contains the MLB.TV window. default: "Google Chrome"
  --title-keyword TITLE_KEYWORD
                        a substring of the MacOS window name to check the status of. default: "MLB.TV Web Player"
  --audio-method AUDIO_METHOD
                        advanced: overrides the method of muting the audio. one of "applescript" or "switchaudio"
  --audio-device AUDIO_DEVICE
                        advanced: custom audio device to control instead of the default system speaker device when using switchaudio mode
  --debug, -d           advanced: enable debug logging
```
