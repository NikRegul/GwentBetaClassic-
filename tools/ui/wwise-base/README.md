# Wwise2023.1.19 project skeleton

Created by the installed WwiseConsole2023.1.19.8928 `create-new-project`,
then saved by its console serializer. No audio media, license key or user
settings are included. The canonical project includes empty pre/post command
properties: deleting these makes Wwise repair the project on load.

`prepare_audio_import.py` copies the skeleton into the private audio project.
It keeps the TW3 project ID, only the Master/Immerse/GUI bus GUID chain,
System audio device and W3 sfx conversion. Additional bank events route to
the game's existing GUI bus. The generated Init.bnk is never installed.

The installed trial allows200 media, established by the console's own fatal
diagnostic on a240-source project. This first import contains200 sources;
expansion requires an appropriate project license, not additional banks
to circumvent the project limit. Source banks/WAV extraction remain intact.
