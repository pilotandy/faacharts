import queue
from classes.vfr.process import ProcessVFR
from classes.web.interface import WebInterface


def main():

    # Spin up the website interface
    web = WebInterface()
    req, res = web.getQueues()
    web.start()

    # Make sure the web interface is ready
    try:
        res.get(timeout=5)

        # Process the VFR charts
        vfr = ProcessVFR(req, res)
        vfr.start()
        vfr.join()

    except queue.Empty:
        print("Main: WebInterface isn't ready. Bye!")

    # Close things up.
    web.stop()
    web.join()


if __name__ == "__main__":
    main()
