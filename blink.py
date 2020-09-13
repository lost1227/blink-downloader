from blinkpy.blinkpy import Blink
from blinkpy.auth import Auth
from blinkpy.helpers.util import json_load

from pathlib import Path

class CustBlink:
    def __init__(self, blink_location, blink_period):
        self.blink_location = blink_location
        self.blink_period = blink_period
        if not blink_location.is_dir():
            blink_location.mkdir()

    def reauth(self):
        self.blink = Blink()

        creds = self.blink_location / "creds.json"
        started = False

        print("Logging in to Blink...")
        if creds.is_file():
            auth = Auth(json_load(creds))
            self.blink.auth = auth
            started = self.blink.start()

        if not started:
            started = self.blink.start()
            if started:
                self.blink.save(creds)

        return started
