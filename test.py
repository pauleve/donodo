
from donodo.docker import DockerImage
from donodo.zenodo import *

di = DockerImage("colomoto/colomoto-docker:2020-08-01")

zs = ZenodoSession(os.getenv("ZENODO_TOKEN"))
zd = ZenodoImageDeposition(zs, di, publication_date=di.tag)

print(di.labels)
print("ok")
