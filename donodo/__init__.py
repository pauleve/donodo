
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def archive(docker_image):
    """
    Archive a docker image on Zenodo
    """
    raise NotImplementedError

def pull(zenodo_doi):
    """
    Retrieve a Docker image from a zenodo record
    """
    raise NotImplementedError

def cli():
    raise NotImplementedError
