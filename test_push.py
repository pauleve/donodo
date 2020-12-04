
import sys

from donodo.docker import DockerImage
from donodo.zenodo import *
from donodo import config

from subprocess import Popen, PIPE

config.deposition_compression = sys.argv[2] if len(sys.argv) > 2 else None

di = DockerImage(sys.argv[1])
zs = ZenodoSession(os.getenv("ZENODO_TOKEN"))
zd = ZenodoImageDeposition(zs, di)
if True or not zd.image_deposit:
    with di.save() as p:
    #with Popen(["cat", "/tmp/test.txt"], stdout=PIPE) as p:
        zd.put_image(p.stdout)
print()
print(zd.edit_link)
print()
answer = input("PUBLISH? (y/N) ")
if answer.lower().startswith("y"):
    print(zd.publish())


