import os
from pathlib import Path
from blink import CustBlink

import signal
import datetime

import threading

import argparse

blink_period = int(os.environ.get("BLINK_PERIOD"))
blink_location = Path(os.environ.get("BLINK_LOCATION"))

parser = argparse.ArgumentParser()
parser.add_argument('--login-only', action='store_true')
args = parser.parse_args()


blink = CustBlink(blink_location, blink_period)

if args.login_only:
    print("Authenticating...")
    authed = blink.login_only()
    if not authed:
        print("Authentication failed")
    else:
        print("Authentication succeeded")
    exit()

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
    authed = blink.reauth()
    if not authed:
        print("Failed to authenticate. Exiting...")
        exit(1)
    print("Downloading videos since ", since)
    blink.blink.download_videos(blink_location / "downloads", since=str(since))
    since += delta
    print("Waiting for {} seconds".format(delta.total_seconds()))
    if interrupt_event.wait(delta.total_seconds()):
        print("Interrupted!")
        break

