# anki-voice
control anki with your voice
--
a little add-on I wrote for myself to use anki hands-free (such as when cooking or something)
command list: good/again/show/stop listening. customize the words for each command in `config.json`


installation:
- clone repo into addons directory
- run `build.sh`
- launch anki

warning!
with my testing on windows, running this add-on will break audio and video in cards (as in they will no longer play). 
my theory is that sounddevice (which is used to capture mic input) uses portaudio on the backend, and I guess that messes with the backend anki uses for audio and video playback.
most of my issues developing this has been portaudio being finnicky.
