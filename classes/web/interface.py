import os
import queue
import requests
import traceback
import multiprocessing

from .auth import Auth


class WebInterface(multiprocessing.Process):
    def __init__(self):
        multiprocessing.Process.__init__(self)
        self.req = None
        self.res = None
        self.exit = multiprocessing.Event()

        self.session = requests.Session()
        self.host = os.environ.get("WEB_HOST")
        self.auth = Auth(self.session)

        self.methods = {
            "GET": self.session.get,
            "POST": self.session.post,
            "PUT": self.session.put,
        }

    def getQueues(self):
        self.req = multiprocessing.Queue()
        self.res = multiprocessing.Queue()
        return (self.req, self.res)

    def request(self, parts):
        try:
            headers = {"Authorization": "Bearer " + self.auth.access()}
            data = None
            if len(parts) > 2:
                data = parts[2]

            r = self.methods[parts[0]](self.host + parts[1], headers=headers, data=data)
            return (r.status_code, r.content)
        except Exception as exc:
            return (500, b"WebInterface: " + str(exc).encode("utf8"))

    def run(self):
        print("WebInterface: Running")
        while not self.exit.is_set():
            try:
                req = self.req.get(timeout=1)
                res = self.request(req)
                self.res.put(res)
            except queue.Empty:
                pass
            except Exception as exc:
                print(
                    "WebInterface: Error: " + str(exc) + "\n" + traceback.format_exc()
                )

    def stop(self):
        print("WebInterface: Stopping")
        self.exit.set()
