import os
import re
import json
import queue
import requests
import traceback
import multiprocessing

from .faacharts import GetCharts, Download


class Process(multiprocessing.Process):
    def __init__(self, charttype, webreq, webres):
        multiprocessing.Process.__init__(self)

        # Queues to communicate with the website process
        self.webreq = webreq
        self.webres = webres

        self.workroot = os.environ.get("WORK_ROOT")
        self.charttype = charttype.lower()

    def run(self):

        # Get the new charts from the FAA website
        new = GetCharts(self.charttype)

        # Get the current charts from our website
        self.webreq.put(["GET", f'/api/flight/chart/?search="{self.charttype}"'])
        status, r = self.webres.get(timeout=10)
        if status != 200:
            print(
                f"Failed to get the {self.charttype.upper()} chart list:",
                r.decode("utf8"),
            )
            return
        current = json.loads(r)

        # Download any changed charts
        path = os.path.join(self.workroot, self.charttype)
        wip = Download(new, current, path, self.webreq, self.webres)

        # Dont commit me!
        wip = []
        for c in current:
            if c["use"]:
                wip.append(c)

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
