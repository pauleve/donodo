
import os

from .docker import *
from .zenodo import *
from donodo import config
from donodo import templates
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def push(image, token, auto_publish=False, force_upload=False):
    """
    Archive a docker image on Zenodo
    """
    di = DockerImage(image)
    zs = ZenodoSession(token)
    zd = ZenodoImageDeposition(zs, di)
    if force_upload or not zd.image_deposit:
        with di.save() as p:
            zd.put_image(p.stdout)
    else:
        logger.info("Image is already uploaded, skipping")
    if not auto_publish:
        print()
        print(zd.edit_link)
        print()
        answer = input("PUBLISH? (y/N) ")
        auto_publish = answer.lower().startswith("y")
    if auto_publish:
        doi_link = zd.publish()
        print(f"Docker image {image} persistently published at:")
        print(doi_link)
        return 0
    return 2

def pull(doi):
    """
    Retrieve a Docker image from a zenodo DOI
    """
    zs = ZenodoAnonymousSession()
    zr = ZenodoImageRecord(zs, doi)
    with zr.open() as fp:
        return docker_load(fp)

def cli():
    from argparse import ArgumentParser
    parser = ArgumentParser(prog=os.path.basename(sys.argv[0]),
        description="Docker <-> Zenodo")
    parser.add_argument("--debug", default="INFO",
                choices={"DEBUG", "INFO", "WARNING", "ERROR"})
    parser.add_argument("--sandbox", action="store_true", default=False,
            help="Use the sandbox of Zenodo")
    subp = parser.add_subparsers(help="command")

    p = subp.add_parser("pull",
            help="Pull Docker image from Zenodo record")
    p.add_argument("doi", help="Zenodo DOI identifier or link")
    p.set_defaults(func="pull")

    p = subp.add_parser("push",
            help="Push a Docker image into a new Zenodo record")
    p.add_argument("image", help="Docker image in the form <name>:<nag>")
    p.add_argument("--auto-publish", action="store_true", default=False,
            help="Publish the record after upload")
    p.add_argument("--compression-mode", default="gz",
            choices={"gz"},
            help="Method for compressing the image")
    p.add_argument("--force-upload", action="store_true", default=False,
            help="Force image (re)upload")
    p.add_argument("--templates",
            help="JSON file overriding templates for deposition")
    p.set_defaults(func="push")

    args = parser.parse_args()

    logger.setLevel(args.debug)
    use_sandbox(args.sandbox)

    if not hasattr(args, "func"):
        return parser.print_help()

    if args.func == "push":
        # Zenodo API token
        token = os.getenv("ZENODO_TOKEN")
        if not token:
            logger.critical("No ZENODO_TOKEN environment variable defined")
            return 1
        # Configuration
        config.deposition_compression = args.compression_mode \
                if args.compression_mode != "none" else None
        # Templates
        if args.templates:
            templates.custom_templates_from_json(args.templates)
        # Push
        return push(args.image, token,
                auto_publish=args.auto_publish,
                force_upload=args.force_upload)

    if args.func == "pull":
        return pull(args.doi)
