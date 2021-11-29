import os
import json
import multiprocessing

from classes.warp import WarpCharts

from .faacharts import GetCharts, Download
from .unzip import UnzipCharts
from .convertrgb import ConvertToRGB
from .warp import WarpCharts
from .crop import CropCharts
from .publish import BuildVRT, MoveToReady, BuildList, GenerateTiles, Publish


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
        charts = Download(new, current, path, self.webreq, self.webres)

        chart_count = len(charts)
        charts = UnzipCharts(charts, path)
        charts = ConvertToRGB(charts, path, self.charttype)
        charts = WarpCharts(charts, path)
        charts = CropCharts(charts, path, self.charttype)

        charts = MoveToReady(charts, path)
        if len(charts) == chart_count:
            if BuildList(path) and BuildVRT(path):
                if GenerateTiles(path):
                    version = charts[0]["version"]
                    Publish(path, version, self.charttype, self.webreq, self.webres)
