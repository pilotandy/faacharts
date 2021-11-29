import queue
from classes.process import Process
from classes.web.interface import WebInterface


def main():

    # Spin up the website interface
    web = WebInterface()
    req, res = web.getQueues()
    web.start()

    # Process the VFR charts
    vfr = Process("vfr", req, res)
    vfr.start()
    vfr.join()

    # Close things up.
    web.stop()
    web.join()


if __name__ == "__main__":
    main()
