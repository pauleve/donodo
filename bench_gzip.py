
from subprocess import Popen, PIPE
import shutil
import sys

from donodo.docker import DockerImage

di = DockerImage(sys.argv[1])

a = di.save()
with a.stdout:
    b = Popen(["gzip", "-c"], stdin=a.stdout, stdout=PIPE)
    with b.stdout, open("/tmp/out.tar.gz", "wb") as fp:
        shutil.copyfileobj(b.stdout, fp)
statuses = [a.wait(), b.wait()] # both a.stdin/stdout are closed already
