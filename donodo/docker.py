
import json
import logging
import os
import platform
import shutil
from subprocess import DEVNULL, call, Popen, PIPE
import sys

logger = logging.getLogger(__name__)

on_linux = platform.system() == "Linux"

def check_cmd(argv):
    try:
        call(argv, stdout=DEVNULL, stderr=DEVNULL, close_fds=True)
        return True
    except:
        return False

def check_sudo():
    return check_cmd(["sudo", "true"])

def docker_call():
    direct_docker = ["docker"]
    sudo_docker = ["sudo", "docker"]
    if on_linux:
        import grp
        try:
            docker_grp = grp.getgrnam("docker")
            if docker_grp.gr_gid in os.getgroups():
                return direct_docker
        except KeyError:
            raise
        if not check_sudo():
            raise Exception("""'sudo' is not installed and you are not in the 'docker' group.
Either install sudo, or add your user to the docker group by doing
   su -c "usermod -aG docker $USER" """)
        return sudo_docker
    return direct_docker

def check_docker():
    if not check_cmd(["docker", "help"]):
        if not on_linux:
            raise Exception("""Docker not found.
If you are using Docker Toolbox, make sure you are running 'colomoto-docker'
within the 'Docker quickstart Terminal'.""")
        else:
            raise Exception("Docker not found")
    return docker_call()

docker_argv = check_docker()

class DockerImage(object):
    def __init__(self, spec):
        if ":" not in spec:
            raise ValueError("The Docker image name should contain a tag")
        name, tag = spec.split(":")
        if tag == "latest":
            raise ValueError("The Docker image tag should be a proper version (not latest)")
        self.name = name
        self.tag = tag
        self.spec = spec
        with Popen(docker_argv + ["inspect", self.spec], stdout=PIPE) as p:
            inspect = json.load(p.stdout)
        assert p.returncode == 0, f"Error inspecting Docker image {spec}. Does it exist?"
        self.inspect = inspect[0]
        self.labels = self.inspect["Config"]["Labels"] or {}

    def save(self):
        return Popen(docker_argv + ["save", self.spec], stdout=PIPE)

def docker_load(fp):
    with Popen(docker_argv + ["load"], stdin=PIPE) as p:
        shutil.copyfileobj(fp, p.stdin)
    return p.returncode
