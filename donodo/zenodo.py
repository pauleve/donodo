
import json
import gzip
import logging
import os
import sys

from gzip_stream import GZIPCompressedStream
import requests

from donodo.templates import deposition_templates, eval_template

logger = logging.getLogger(__name__)

class ZenodoSession(object):
    base_url = "https://sandbox.zenodo.org/api"

    def __init__(self, token):
        self.token = token

    def request(self, method, url="", params={}, raw_url=False, **kwargs):
        params["access_token"] = self.token
        if not raw_url:
            url = self.base_url + url
        logger.debug((url, kwargs))
        ret = getattr(requests, method)(url, params=params, **kwargs)
        if ret.status_code != 204:
            ret = ret.json()
        if isinstance(ret, dict) and ret.get("status",0) >= 400:
            logger.critical(ret)
            sys.exit(1)
        return ret

    def get(self, *args, **kwargs):
        return self.request("get", *args, **kwargs)
    def post(self, *args, **kwargs):
        return self.request("post", *args, **kwargs)
    def put(self, *args, **kwargs):
        return self.request("put", *args, **kwargs)
    def delete(self, *args, **kwargs):
        return self.request("delete", *args, **kwargs)


class ZenodoSubSession(ZenodoSession):
    def __init__(self, parent, subpath):
        super().__init__(parent.token)
        self.base_url = parent.base_url + subpath


class ZenodoDeposition(object):
    def __init__(self, zs, deposit):
        self.deposit = deposit
        if deposit["submitted"]:
            logger.critical("The record for this image is already published")
            sys.exit(1)
        self.id = deposit["id"]
        self.zs = ZenodoSubSession(zs, f"/deposit/depositions/{self.id}")

    def list_files(self):
        return self.zs.get("/files")

    @property
    def edit_link(self):
        return self.deposit["links"]["html"]

    def update(self, data):
        data = json.dumps(data)
        headers = {"Content-Type": "application/json"}
        self.deposit = self.zs.put(data=data, headers=headers)

    def put_file(self, filename, fp):
        bucket = self.deposit["links"]["bucket"]
        headers = {"Accept": "application/json", "Content-Type": "application/octet-stream"}
        return self.zs.put(f"{bucket}/{filename}", raw_url=True,
                    data={"file": fp}, headers=headers)

    def publish(self):
        self.deposit = self.post("/actions/publish")
        return self.deposit["doi_url"]

class ZenodoImageDeposition(ZenodoDeposition):
    image_filename = "image.tar"

    def __init__(self, zs, image, **metadata):
        _meta = {entry: eval_template(tmpl, image=image)
            for entry, tmpl in deposition_templates.items()}
        _meta.update(metadata)
        if "keywords" in _meta:
            _meta["keywords"] = [k.strip() for k in _meta["keywords"].split(";")]

        title = _meta["title"]
        version = _meta["version"]

        matches = zs.get("/deposit/depositions", {"q": f'"{title}"'})
        matches = [m for m in matches if m["title"] == title]
        if not matches:
            logger.info("no matching deposition, create new")
            deposit = zs.post("/deposit/depositions", {}, json={})
        else:
            p = matches[0]
            matches = zs.get("/deposit/depositions", { "q":
                f"conceptrecid:{p['conceptrecid']} AND version:{version}",
                "all_versions": 1})
            if matches:
                # resume version
                deposit = matches[0]
            else:
                # new version
                p = zs.post(f"/deposit/depositions/{p['id']}/actions/newversion")
                deposit = zs.get(p["links"]["latest_draft"], raw_url=True)
        super().__init__(zs, deposit)
        self.update({"metadata": _meta})
        self.image = image

    @property
    def image_deposit(self):
        existing = [f for f in self.list_files()
                        if f["filename"] == self.image_filename]
        if existing:
            return existing[0]

    def put_image(self, fp):
        existing = self.image_deposit
        if existing:
            logger.info("Image file already exists, deleting first..")
            self.zs.delete(f"/files/{existing['id']}")
        print("Uploading image, this may take a while...")
        #fp = GZIPCompressedStream(fp, compression_level=6)
        self.put_file(self.image_filename, fp)
        print("Done!")


class ZenodoRecord(object):
    def __init__(self, zs, doi):
        matches = zs.get("/records", {"q": f"doi:{doi.replace('/','//')}"})
        if not matches:
            logger.critical("No Zenodo record for DOI {doi}")
            sys.exit(1)
        assert len(matches) == 1
        self.record = matches[0]

    def list_files(self):
        pass

    def entry(self):
        pass

class ZenodoImageRecord(ZenodoRecord):
    pass
