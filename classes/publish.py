import os
import glob
import shutil
import subprocess


def MoveToReady(charts, path):
    wippath = os.path.join(path, "wips")
    readypath = os.path.join(path, "ready")
    os.makedirs(readypath, exist_ok=True)

    print(f"Finalizing {len(charts)} charts:")

    ready = []
    for chart in charts:
        try:
            log = [f"Moving {chart['name']} to READY..."]
            cropname = os.path.join(wippath, chart["name"] + ".crop.tif")
            readyname = os.path.join(readypath, chart["name"] + ".tif")
            shutil.move(cropname, readyname)
            log[0] += "done."
        except Exception as exc:
            log.append(str(exc))
            chart = None

        print("    ", end="")
        print(log[0])
        for l in log[1:]:
            print("        ", end="")
            print(l)

        if chart:
            ready.append(chart)

    return ready


def BuildList(path):
    print("Building Image List for Mosaic...")
    readypath = os.path.join(path, "ready")
    lstpath = os.path.join(readypath, "mosaic.lst")
    tiffiles = sorted(glob.glob(readypath + "/*.tif"))
    with open(lstpath, "w") as lst:
        for f in tiffiles:
            lst.write(f + "\n")

    return True


def BuildVRT(path):
    readypath = os.path.join(path, "ready")

    print("Analyzing...")
    lst = os.path.join(readypath, "mosaic.lst")
    vrt = os.path.join(readypath, "mosaic.vrt")

    cmd = [
        "gdalbuildvrt",
        "-hidenodata",
        "-vrtnodata",
        '"229 227 223"',
        "-input_file_list",
        lst,
        vrt,
    ]
    p = subprocess.run(
        " ".join(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    if p.returncode != 0:
        print(" ".join(cmd))
        msg = p.stdout.decode("utf8")
        print(msg)
        return False

    return True


def GenerateTiles(path):
    readypath = os.path.join(path, "ready")
    temppath = os.path.join(path, "temp")
    if os.path.exists(temppath):
        shutil.rmtree(temppath)
    os.makedirs(temppath, exist_ok=True)

    vrt = os.path.join(readypath, "mosaic.vrt")

    print("Generating Tiles...")
    scriptpath = os.path.abspath(os.path.dirname(__file__))
    scriptpath = os.path.join(scriptpath, "gdal2tiles_parallel.py")

    cmd = [
        "python",
        scriptpath,
        "-r",
        "cubic",
        "-t",
        '"PilotAndy Maps"',
        "--zoom",
        "05-11",
        "-u",
        "http://www.pilotandy.com/maptiles/",
        vrt,
        temppath,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode != 0:
        print(" ".join(cmd))
        msg = p.stdout.decode("utf8")
        print(msg)
        return False


def Publish(path):
    pass
