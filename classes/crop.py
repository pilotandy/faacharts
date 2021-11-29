import os
import subprocess
import multiprocessing


def CropChart(chart, path, shppath):
    wippath = os.path.join(path, "wips")

    warpname = os.path.join(wippath, chart["name"] + ".warp.tif")
    cropname = os.path.join(wippath, chart["name"] + ".crop.tif")
    shpfile = os.path.join(shppath, chart["name"] + "SEC.shp")

    log = ["Cropping " + chart["name"] + ".warp.tif" + "..."]
    cmd = [
        "gdalwarp",
        "-cutline",
        shpfile,
        "-crop_to_cutline",
        "-srcnodata",
        '"123 123 123"',
        "-dstnodata",
        '"123 123 123"',
        "-of GTiff",
        "-overwrite",
        warpname,
        cropname,
    ]

    p = subprocess.run(
        " ".join(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    if p.returncode == 0:
        if os.path.exists(cropname) and os.stat(cropname).st_size > 0:
            log[0] += "done."
            os.remove(warpname)
        else:
            log.append("The CROP tif doesn't exist, or is zero bytes!")
            chart = None
    else:
        msg = p.stdout.decode("utf8")
        msg = msg.split("\n")
        log.append(" ".join(cmd))
        log += msg
        chart = None

    return (chart, log)


def CropCharts(charts, path, charttype):
    print(f"Croping {len(charts)} charts:")

    shppath = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    shppath = os.path.join(shppath, "shapes", charttype)

    work = [(c, path, shppath) for c in charts]
    p = multiprocessing.Pool(4)
    results = p.starmap(CropChart, work)
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
