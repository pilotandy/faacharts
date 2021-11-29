import os
import re
import zipfile
import multiprocessing


def UnzipChart(chart, path):
    zippath = os.path.join(path, "zips")
    wippath = os.path.join(path, "wips")
    os.makedirs(wippath, exist_ok=True)

    log = ["Extracting " + chart["name"] + ".tif" + "..."]
    try:
        zf = os.path.join(zippath, chart["name"] + ".zip")
        with zipfile.ZipFile(zf, "r") as zip:
            for f in zip.namelist():
                if os.path.splitext(f)[1] == ".tif":
                    tif = re.sub(r"[ \d]", "", f).replace("SEC", "")
                    tifpath = os.path.join(wippath, tif)
                    with zip.open(f, "r") as zh:
                        with open(tifpath, "wb") as th:
                            th.write(zh.read())
        log[0] += "done."
    except Exception as exc:
        log.append("Exception: " + str(exc))
        chart = None

    return (chart, log)


def UnzipCharts(charts, path):
    print(f"Extracting {len(charts)} charts:")
    work = [(c, path) for c in charts]
    p = multiprocessing.Pool(4)
    results = p.starmap(UnzipChart, work)
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
