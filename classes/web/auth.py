import os
import json


class Auth:
    def __init__(self, session):
        self.session = session
        self.tokens = None
        self.host = os.environ.get("WEB_HOST")
        self.user = os.environ.get("WEB_USER")
        self.passwd = os.environ.get("WEB_PASS")

    def login(self):
        r = self.session.post(
            self.host + "/jwt/token/",
            data={"email": self.user, "password": self.passwd},
        )
        if r.status_code != 200:
            res = json.loads(r.content)
            raise Exception(res.get("detail", r.content))
        self.tokens = json.loads(r.content)

    def refresh(self):
        r = self.session.post(
            self.host + "/jwt/token/refresh",
            data={"refresh": self.token.get("refresh")},
        )
        if r.status_code != 200:
            self.login()
        else:
            self.tokens = json.loads(r.content)

    def access(self):
        if self.tokens is None:
            self.login()
        return self.tokens["access"]
