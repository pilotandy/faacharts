import os
import subprocess
import multiprocessing


def ConvertVFRToRGB(chart, path):
    wippath = os.path.join(path, "wips")

    tifname = os.path.join(wippath, chart["name"] + ".tif")
    rgbname = os.path.join(wippath, chart["name"] + ".rgb.tif")

    log = ["Converting " + chart["name"] + ".tif" + " to RGB..."]
    cmd = [
        "gdal_translate",
        "-q",
        "-expand",
        "rgb",
        "-co",
        "TILED=YES",
        "-of",
        "GTiff",
        "-a_nodata",
        '"123 123 123"',
        tifname,
        rgbname,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode == 0:
        if os.path.exists(rgbname) and os.stat(rgbname).st_size > 0:
            log[0] += "done."
            os.remove(tifname)
        else:
            log.append("The RGB tif doesn't exist, or is zero bytes!")
            chart = None
    else:
        msg = p.stdout.decode("utf8")
        msg = msg.split("\n")
        log += msg
        chart = None

    return (chart, log)


def ConvertIFRToRGB(chart, path):
    wippath = os.path.join(path, "wips")

    tifname = os.path.join(wippath, chart["name"] + ".tif")
    rgbname = os.path.join(wippath, chart["name"] + ".rgb.tif")

    log = ["Converting " + chart["name"] + ".tif" + " to RGB..."]
    cmd = [
        "gdal_translate",
        "-q",
        "-co",
        "TILED=YES",
        "-of",
        "GTiff",
        "-a_nodata",
        '"123 123 123"',
        tifname,
        rgbname,
    ]
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if p.returncode == 0:
        if os.path.exists(rgbname) and os.stat(rgbname).st_size > 0:
            log[0] += "done."
            os.remove(tifname)
        else:
            log.append("The RGB tif doesn't exist, or is zero bytes!")
            chart = None
    else:
        msg = p.stdout.decode("utf8")
        msg = msg.split("\n")
        log += msg
        chart = None

    return (chart, log)


conversions = {"vfr": ConvertVFRToRGB, "ifr": ConvertIFRToRGB}


def ConvertToRGB(charts, path, charttype):
    print(f"Converting {len(charts)} charts to RGB:")
    work = [(c, path) for c in charts]
    p = multiprocessing.Pool(4)
    results = p.starmap(conversions[charttype], work)
    charts = []
    for result in results:
        chart, log = result
        if chart:
            charts.append(chart)
        print("    ", end="")
        print(log[0])
        for l in log[1:]:
            print("        ", end="")
            print(l)
    p.close()
    p.join()

    return charts
