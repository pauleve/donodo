
from setuptools import setup, find_packages

setup(name="donodo",
    version = "9999",
    license = "MIT",
    author = "Loïc Paulevé",
    author_email = "loic.pauleve@labri.fr",
    url = "https://github.com/pauleve/donodo",
    description = "Bridging Docker images with Zenodo",
    packages = find_packages(),
    entry_points = {
        "console_scripts": [
            "donodo = donodo:cli"
        ]
    },
    install_requires = [
        "requests",
    ]
)
