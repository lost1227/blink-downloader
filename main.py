import os
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from pathlib import Path

import signal
import datetime
import time

blink_period = int(os.environ.get("BLINK_PERIOD"))
blink_location = Path(os.environ.get("BLINK_LOCATION"))

if not blink_location.is_dir():
    blink_location.mkdir()

creds = blink_location / "creds.json"

blink = Blink()

started = False

print("Logging in to Blink...")
if creds.is_file():
    auth = Auth(json_load(creds))
    blink.auth = auth
    started = blink.start()

if not started:
    started = blink.start()
    if started:
        blink.save(creds)

if not started:
    print("Could not log in. Exiting...")
    exit(1)

since = datetime.datetime.now()
delta = datetime.timedelta(seconds=blink_period)
since -= delta

interrupted = False
def handle():
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, handle)
signal.signal(signal.SIGTERM, handle)

while not interrupted:
    print("Downloading videos since ", since)
    blink.download_videos(blink_location / "downloads", since=str(since))
    since += delta
    time.sleep(delta.total_seconds())

