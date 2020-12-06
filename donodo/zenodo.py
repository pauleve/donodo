
import json
import gzip
import logging
import os
from subprocess import Popen, PIPE
import sys
from urllib.parse import urlparse
from urllib.request import urlopen

import requests

from donodo.templates import deposition_templates, eval_template
from donodo import config

logger = logging.getLogger(__name__)

def use_sandbox(sandbox):
    if sandbox:
        ZenodoSession.base_url = "https://sandbox.zenodo.org/api"
    else:
        ZenodoSession.base_url = "https://zenodo.org/api"

class ZenodoSession(object):
    base_url = "https://sandbox.zenodo.org/api"

    def __init__(self, token=None, session=None):
        self.session = requests.Session() if session is None else session
        if token:
            self.session.params["access_token"] = token

    def request(self, method, url="", raw_url=False, **kwargs):
        if not raw_url:
            url = self.base_url + url
        logger.debug((url, kwargs))
        ret = getattr(self.session, method)(url, **kwargs)
        if ret.status_code != 204:
            ret = ret.json()
        if isinstance(ret, dict) and ret.get("status",0) >= 400:
            logger.critical(ret)
            raise Exception(ret)
        return ret

    def get(self, *args, **kwargs):
        return self.request("get", *args, **kwargs)
    def post(self, *args, **kwargs):
        return self.request("post", *args, **kwargs)
    def put(self, *args, **kwargs):
        return self.request("put", *args, **kwargs)
    def delete(self, *args, **kwargs):
        return self.request("delete", *args, **kwargs)

class ZenodoAnonymousSession(ZenodoSession):
    def __init__(self):
        super().__init__(None)

class ZenodoSubSession(ZenodoSession):
    def __init__(self, parent, subpath):
        super().__init__(session=parent.session)
        self.base_url = parent.base_url + subpath


class ZenodoDeposition(object):
    def __init__(self, zs, deposit):
        self.deposit = deposit
        if deposit["submitted"]:
            raise ValueError("The record for this image is already published")
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
        return self.zs.put(f"{bucket}/{filename}", raw_url=True, data=fp)

    def publish(self):
        self.deposit = self.zs.post("/actions/publish")
        return self.deposit["doi_url"]

class ZenodoImageDeposition(ZenodoDeposition):
    image_filename = "image.tar"

    def __init__(self, zs, image, **metadata):
        _meta = {entry: eval_template(tmpl, image=image)
            for entry, tmpl in deposition_templates.items()}
        _meta.update(metadata)

        title = _meta["title"]
        version = _meta["version"]

        matches = zs.get("/deposit/depositions", params={"q": f'"{title}"'})
        matches = [m for m in matches if m["title"] == title]
        clear_image = False
        if not matches:
            logger.info("no matching deposition, create new")
            deposit = zs.post("/deposit/depositions", json={})
        else:
            p = matches[0]
            matches = zs.get("/deposit/depositions", params={ "q":
                f"conceptrecid:{p['conceptrecid']} AND version:{version}",
                "all_versions": 1})
            if matches:
                # resume version
                deposit = matches[0]
            elif p["state"] == "unsubmitted":
                # resume with different version
                deposit = p
                clear_image = True
            else:
                # new version
                p = zs.post(f"/deposit/depositions/{p['id']}/actions/newversion")
                deposit = zs.get(p["links"]["latest_draft"], raw_url=True)
                clear_image = True
        super().__init__(zs, deposit)
        self.update({"metadata": _meta})
        self.image = image
        if clear_image:
            self.delete_image()

    @property
    def image_deposit(self):
        return [f for f in self.list_files()
                        if f["filename"].startswith(self.image_filename)]

    def delete_image(self):
        existing = self.image_deposit
        if existing:
            logger.info("Image file already exists, deleting first..")
            for f in existing:
                self.zs.delete(f"/files/{f['id']}")

    def put_image(self, fp):
        self.delete_image()

        logger.info("Uploading image, this may take a while...")

        if config.deposition_compression == "gz":
            import shutil
            import tempfile
            with tempfile.TemporaryFile() as tmpfp:
                with gzip.GzipFile(mode="wb", fileobj=tmpfp) as gzfp:
                    shutil.copyfileobj(fp, gzfp)
                tmpfp.seek(0)
                self.put_file(self.image_filename+".gz", tmpfp)

        else:
            raise ValueError(f"unknown compression method '{config.deposition_compression}'")

        logger.info("Done!")


class ZenodoRecord(object):
    def __init__(self, zs, doi):
        doi = urlparse(doi).path.strip('/')
        if doi.startswith("record/"): # this is actually a record url
            record_id = doi.split("/")[1]
            self.record = zs.get(f"/records/{record_id}")
        else:
            r = zs.get("/records", params={"q": "doi:{}".format(doi.replace('/','\\/')),
                    "all_versions": 1})
            matches = r["hits"]["hits"]
            if not matches:
                raise KeyError(f"No Zenodo record for DOI {doi}")
            assert len(matches) == 1
            self.record = matches[0]
        self.doi = self.record["doi"]


class ZenodoImageRecord(ZenodoRecord):
    def __init__(self, zs, doi):
        super().__init__(zs, doi)
        self.image_file = self._locate_image()

    def _locate_image(self):
        files = self.record["files"]
        # 1. find a filename starting with image.tar
        images = [f for f in files if f["key"].startswith("image.tar")]
        if not images:
            # 2. find a filename contains .tar
            images = [f for f in files if ".tar" in f["key"]]
        if not images:
            raise KeyError(f"Zenodo record {self.doi} does not contain a Docker image")
        assert len(images) == 1, "multiple image candidates!"
        return images[0]

    def open(self):
        url = self.image_file["links"]["self"]
        logger.info(f"Downloading {url}")
        fp = urlopen(url)
        if self.image_file["type"] == "gz":
            fp = gzip.GzipFile(fileobj=fp)
        return fp
