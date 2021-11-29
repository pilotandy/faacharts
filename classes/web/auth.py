import os
import jwt
import json
import time


JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")


def get_exptime(token):
    return int(jwt.decode(token, JWT_SECRET_KEY, algorithms="HS256")["exp"]) - 60


class Auth:
    def __init__(self, session):
        self.session = session
        self.host = os.environ.get("WEB_HOST")
        self.user = os.environ.get("WEB_USER")
        self.passwd = os.environ.get("WEB_PASS")
        self.tokens = None
        self.access_expires = 0
        self.refresh_expires = 0

    def login(self):
        r = self.session.post(
            self.host + "/jwt/token/",
            data={"email": self.user, "password": self.passwd},
        )
        if r.status_code != 200:
            res = json.loads(r.content)
            raise Exception(res.get("detail", r.content))
        self.tokens = json.loads(r.content)
        self.access_expires = get_exptime(self.tokens["access"])
        self.refresh_expires = get_exptime(self.tokens["refresh"])

    def refresh(self):
        if time.time() > self.refresh_expires:
            self.login()
        else:
            r = self.session.post(
                self.host + "/jwt/token/refresh/",
                data={"refresh": self.tokens["refresh"]},
            )
            if r.status_code != 200:
                self.login()
            else:
                self.tokens["access"] = json.loads(r.content)["access"]
                self.access_expires = get_exptime(self.tokens["access"])

    def access(self):
        if time.time() > self.access_expires:
            self.refresh()
        return self.tokens["access"]
