import os
import re
import json
import queue
import requests
import traceback
import multiprocessing

from ..faacharts import GetVFR, Download


class ProcessVFR(multiprocessing.Process):
    def __init__(self, webreq, webres):
        multiprocessing.Process.__init__(self)

        # Queues to communicate with the website process
        self.webreq = webreq
        self.webres = webres

        self.workroot = os.environ.get("WORK_ROOT")

    def run(self):

        # Get the new charts from the FAA website
        new = GetVFR()

        # Get the current charts from our website
        self.webreq.put(["GET", '/api/flight/chart/?search="vfr"'])
        status, r = self.webres.get(timeout=10)
        if status != 200:
            print("Failed to get the VFR chart list:", r.decode("utf8"))
            return
        current = json.loads(r)

        # Download any changed charts
        path = os.path.join(self.workroot, "vfr")
        wip = Download(new, current, path, self.webreq, self.webres)

        print(wip)
        # Unzip(path, wip)

        # Process WIP charts

        # Unzip(maptype["type"])
        # ConvertToRGB(maptype["type"])
        # WarpTo3857(maptype["type"])
        # Crop(maptype["type"])
        # if MoveToReady(maptype["type"]):
        #     BuildList(maptype["type"])
        #     GenerateTiles(maptype["type"])
        #     Publish(maptype["type"])
