import queue
from classes.vfr.process import ProcessVFR
from classes.web.interface import WebInterface


def main():

    # Spin up the website interface
    web = WebInterface()
    req, res = web.getQueues()
    web.start()

    # Process the VFR charts
    vfr = ProcessVFR(req, res)
    vfr.start()
    vfr.join()

    # Close things up.
    web.stop()
    web.join()


if __name__ == "__main__":
    main()
