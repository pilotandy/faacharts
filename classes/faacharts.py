import os
import re
import json
import time
import shutil
import requests
import traceback
import multiprocessing
from bs4 import BeautifulSoup

from .utils import utils

import random


def GetVFR():
    print("Getting published file list VFR...")

    charts = []

    url = "https://www.faa.gov/air_traffic/flight_info/aeronav/digital_products/vfr/"
    doc = requests.get(url).content
    soup = BeautifulSoup(doc, "html.parser")
    caption = soup.find(
        string=re.compile(r"Sectional Aeronautical Raster Charts")
    ).parent
    tbody = caption.find_next_sibling("tbody")
    for tr in tbody.find_all("tr"):
        td = tr.find_all("td")[1]
        anchor = td.find("a")
        link = anchor["href"]

        name = re.search("([^\/]+)\.zip$", link).group(1)
        name = name.replace("_", "")

        v = re.search(r"^.*(\d\d)-(\d\d)-(\d{4}).*$", link)
        version = int(v.group(3) + v.group(1) + v.group(2))

        chart = {
            "charttype": "vfr",
            "name": name,
            "version": version,
            "use": False,
            "link": link,
        }
        charts.append(chart)

    return charts


def DownloadFile(link, path):
    log = ["Downloading " + link["name"] + ".zip..."]

    try:
        # Create folder
        os.makedirs(path, exist_ok=True)

        # Filenames
        partial = os.path.join(path, link["name"] + ".partial")
        fullzip = os.path.join(path, link["name"] + ".zip")

        # Save from web to partial
        dl = 0
        speed = 0
        res = requests.get(link["link"], stream=True)
        start = time.time()
        with open(partial, "wb") as f:
            for chunk in res.iter_content(chunk_size=1024):
                if chunk:
                    end = time.time()
                    dl += len(chunk)
                    speed = (dl / (end - start)) / len(chunk)
                    f.write(chunk)
        del res

        # Update the log with the size and speed
        log[0] = log[0] + "Done."
        b = f"{utils.humanbytes(dl)}"
        b = " " * (10 - len(b)) + b
        s = f"{int(speed)}KB/s"
        log[0] = log[0] + " " * (50 - len(log[0])) + b + " @ " + s

        # Move to zip file
        shutil.move(partial, fullzip)

        # Write update to website.
        DownloadFile.req.put(["PUT", f"/api/flight/chart/{link['id']}/", link])
        status, r = DownloadFile.res.get(timeout=10)
        if status != 200:
            log.append(r.decode("utf8"))

    except:
        msg = traceback.format_exc()
        msg = msg.split("\n")
        log += msg

    return log


def DownloadFileInit(req, res):
    DownloadFile.req = req
    DownloadFile.res = res


def Download(newcharts, oldcharts, path, req, res):

    downloadlinks = []
    for n in newcharts:
        found = False
        for o in oldcharts:
            if o["name"] == n["name"]:
                found = True
                if o["use"]:
                    if o["version"] < n["version"]:
                        n["id"] = o["id"]
                        n["use"] = True
                        downloadlinks.append(n)
        if not found:
            # Add it to the database
            print("Adding to charts <" + n["charttype"] + ">: " + n["name"])

            # Use it and download it if we have the shape file
            head, tail = os.path.split(path)
            shape_post = ""
            if (
                tail == "vfr"
            ):  # Maybe we can remove the "SEC" from VFR shape files in the future
                shape_post = "SEC"
            shape_path = os.path.abspath(os.path.dirname(__file__))
            shape_path = os.path.join(
                shape_path, tail, "shapes", n["name"] + shape_post + ".shp"
            )
            if os.path.exists(shape_path):
                n["use"] = True

            # POST it to the website
            link = n["link"]
            req.put(["POST", "/api/flight/chart/", n])
            status, r = res.get()
            if status == 201:
                chart = json.loads(r)
                if chart["use"]:
                    chart["link"] = link
                    downloadlinks.append(chart)
            else:
                print(r.decode("utf8"))

    print("    Downloads to process: " + str(len(downloadlinks)))
    zippath = os.path.join(path, "zips")
    work = [(l, zippath) for l in downloadlinks]
    p = multiprocessing.Pool(4, DownloadFileInit, [req, res])
    results = p.starmap(DownloadFile, work)

    for result in results:
        print("        ", end="")
        print(result[0])
        for r in result[1:]:
            print("            ", end="")
            print(r)

    p.close()
    p.join()

    return downloadlinks
