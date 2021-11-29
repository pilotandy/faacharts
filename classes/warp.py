import os
import subprocess
import multiprocessing


def WarpChart(chart, path):
    wippath = os.path.join(path, "wips")

    rgbname = os.path.join(wippath, chart["name"] + ".rgb.tif")
    warpname = os.path.join(wippath, chart["name"] + ".warp.tif")

    log = ["Warping " + chart["name"] + ".rgb.tif" + " to EPSG:3857..."]
    cmd = [
        "gdalwarp",
        "-q",
        "-t_srs",
        '"EPSG:3857"',
        "-r",
        "bilinear",
        "-co",
        "TILED=YES",
        "-srcnodata",
        '"123 123 123"',
        "-dstnodata",
        '"123 123 123"',
        "-of",
        "GTiff",
        "-overwrite",
        rgbname,
        warpname,
    ]

    p = subprocess.run(
        " ".join(cmd), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True
    )
    if p.returncode == 0:
        if os.path.exists(warpname) and os.stat(warpname).st_size > 0:
            log[0] += "done."
            os.remove(rgbname)
        else:
            log.append("The WARP tif doesn't exist, or is zero bytes!")
            chart = None
    else:
        msg = p.stdout.decode("utf8")
        msg = msg.split("\n")
        log.append(" ".join(cmd))
        log += msg
        chart = None

    return (chart, log)


def WarpCharts(charts, path):
    print(f"Warping {len(charts)} charts to EPSG:3857:")
    work = [(c, path) for c in charts]
    p = multiprocessing.Pool(4)
    results = p.starmap(WarpChart, work)
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
