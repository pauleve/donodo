
import json
import os

from donodo import templates
from .ui import *

import requests

class ZenodoSession(object):
    base_url = "https://sandbox.zenodo.org/api"
    def __init__(self, token):
        self.token = token

    def request(self, method, url="", params={}, **kwargs):
        params["access_token"] = self.token
        if "data" in kwargs:
            if isinstance(kwargs["data"], dict):
                kwargs["data"] = json.dumps(kwargs["data"])
                kwargs["headers"] = {"Content-Type": "application/json"}
        url = self.base_url + url
        print(url, kwargs)
        ret = getattr(requests, method)(url, params=params, **kwargs).json()
        if isinstance(ret, dict) and ret.get("status",0) >= 400:
            error(ret)
        return ret

    def get(self, *args, **kwargs):
        return self.request("get", *args, **kwargs)
    def post(self, *args, **kwargs):
        return self.request("post", *args, **kwargs)
    def put(self, *args, **kwargs):
        return self.request("put", *args, **kwargs)

class ZenodoSubSession(ZenodoSession):
    def __init__(self, parent, subpath):
        super().__init__(parent.token)
        self.base_url = parent.base_url + subpath


class ZenodoDeposition(object):
    def __init__(self, zs, deposit):
        self.deposit = deposit
        self.id = deposit["id"]
        self.zs = ZenodoSubSession(zs, f"/deposit/depositions/{self.id}")

    def update(self, data):
        self.deposit = self.zs.put(data=data)

    def put_file(self):
        pass

    def freeze(self):
        pass

class ZenodoImageDeposition(ZenodoDeposition):
    def __init__(self, zs, image, **metadata):

        title = templates.deposition_title.format(image=image)

        _metadata = {
            "title": title,
            "description": templates.deposition_description.format(image=image),
            "version": image.tag,
            "upload_type": "other",
        }
        _metadata.update(metadata)

        matches = zs.get("/deposit/depositions", {"q": f'"{title}"'})
        matches = [m for m in matches if m["title"] == title]
        if not matches:
            info("no matching deposition, create new")
            deposit = zs.post("/deposit/depositions", {}, json={})
        else:
            p = matches[0]
            matches = zs.get("/deposit/depositions", { "q":
                f"conceptrecid:{p['conceptrecid']} AND version:{image.tag}",
                "all_versions": 1})
            if matches:
                deposit = matches[0]
            else:
                raise NotImplementedError
        super().__init__(zs, deposit)
        self.update({"metadata": _metadata})

class ZenodoRecord(object):
    def __init__(self):
        pass

    def list_files(self):
        pass

    def entry(self):
        pass


class ZenodoImageRecord(ZenodoRecord):
    pass

