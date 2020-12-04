[![PyPI version](https://badge.fury.io/py/donodo.svg)](https://badge.fury.io/py/donodo)

# donodo - Bridging Docker images with Zenodo

## Installation

```sh
pip install -U donodo
```

## Quick usage guide

### Retrieve a Docker image from a Zenodo record
```sh
donodo pull DOI
```
where `DOI` is the Zenodo DOI or link to the record.

### Persistently store a Docker image on Zenodo

```sh
 export ZENODO_TOKEN=your_Zenodo_API_token
donodo push your/image:tag
```

See `donodo push -h` for options.
