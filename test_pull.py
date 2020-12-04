
import sys
import shutil

from donodo.docker import docker_load
from donodo.zenodo import *

from subprocess import *

doi = sys.argv[1] if len(sys.argv) > 1 else "https://doi.org/10.5072/zenodo.707887"

zs = ZenodoAnonymousSession()
zr = ZenodoImageRecord(zs, doi)
with zr.open() as fp:
    ret = docker_load(fp)
sys.exit(ret)
