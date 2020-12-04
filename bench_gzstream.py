from gzip_stream import GZIPCompressedStream
from subprocess import Popen, PIPE
import shutil
import sys

from donodo.docker import DockerImage

di = DockerImage(sys.argv[1])

a = di.save()
with a:
    b = GZIPCompressedStream(a.stdout, compression_level=6)
    with open("/tmp/out2.tar.gz", "wb") as fp:
        shutil.copyfileobj(b, fp)
a.wait()

