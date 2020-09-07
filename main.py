import os
from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load
from pathlib import Path

import signal
import datetime

import threading

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

interrupt_event = threading.Event()

interrupted = False
def handle(signum, stackframe):
    global interrupted
    global interrupt_event
    interrupted = True
    interrupt_event.set()

signal.signal(signal.SIGINT, handle)
signal.signal(signal.SIGTERM, handle)

downloaddir = blink_location / "downloads"
if not downloaddir.is_dir():
    downloaddir.mkdir()

while not interrupted:
    print("Downloading videos since ", since)
    blink.download_videos(blink_location / "downloads", since=str(since))
    since += delta
    print("Waiting for {} seconds".format(delta.total_seconds()))
    if interrupt_event.wait(delta.total_seconds()):
        print("Interrupted!")
        break

