
import sys

from donodo.docker import DockerImage
from donodo.zenodo import *
from donodo import config

config.deposition_compression = sys.argv[2] if len(sys.argv) > 2 else None

di = DockerImage(sys.argv[1])
zs = ZenodoSession(os.getenv("ZENODO_TOKEN"))
zd = ZenodoImageDeposition(zs, di)
if True or not zd.image_deposit:
    with di.save() as fp:
        zd.put_image(fp.stdout)
print(zd.edit_link)
