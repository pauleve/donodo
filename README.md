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

### Zenodo sandbox

Use `donodo --sandbox` to act on the sandbox https://sandbox.zenodo.org.

## Documentation

### `donodo pull`: import a Docker image from a Zenodo record

The `donodo pull` command takes as additional argument either a DOI, a DOI link, or a Zenodo record link.

The command looks by priority for (1) a file whose name starts with `image.tar` (2) a file whose name contains `.tar`.
The filename can ends with either `.tar` or `.tar.gz`.

Whenever a single file is found, it will be downloaded and sent to the `docker load` command; otherwise an error is thrown.

Note that the name and tag of the Docker image are specified within the image file. It will be displayed at the end of the process.

### `donodo push`: export a Docker image as a permament Zenodo record

The `donodo push` commands takes as additional argument the name of the Docker image, including tag (which cannot be `latest`). The Docker image has to exist locally.

The command will create a new record with the title being by default `Docker image {image_name}`. If such a record already exists, it will create a new version of it with the tag of the Docker image.
Thus if you push several tags of the same image name, only a single record will be created, with different versions.

The Docker image is exported using the `docker save` command and compressed in a local temporary file. The file is then uploaded to the Zenodo record as `image.tar.gz`.

Once the draft record has been created, the command will display the link to the draft and ask whether to publish it.
You can modify the record from the webpage if necessary before answering the question. 
The option `--auto-publish` skips this question and promptly publishes the image.

Once published, the command will display its DOI link.

:warning: Once published, the image file cannot be deleted or modified. Note that, however, it remains possible to update the metadata and description of the record.

The `push` command requires a Zenodo API token, given in the `ZENODO_TOKEN` environment variable. You can create an API token at https://zenodo.org/account/settings/applications/ with the deposit:write and deposit:actions scopes.

#### Customize the template of the deposition

The templates used to fill the fields of the Zenodo deposition are specified by the `deposition_templates` variable in [donodo/templates.py](https://github.com/pauleve/donodo/blob/main/donodo/templates.py).
The templates will be interpreted as Python [f-string](https://docs.python.org/3/reference/lexical_analysis.html#f-strings), and have access to the variable `image` which is a `DockerImage` object having the following fields:
- `image.name` being the name of the Docker image
- `image.tag` being the tag of the Docker image
- `image.labels` being a dictionnary of the labels specified in the Docker image
- `image.inspect` being the dictionnary as returned by the `docker inspect` command.

The templates can be overriden using a JSON file given with the option `--templates`.

Example: `docker push --templates mytemplates.json my/image:v1`  with `mytemplates.json` being
```json
{
 "creators": [{"name":"Smith, Jane", "affiliation": "My University", "orcid": "0000-0002-1694-233X"}],
 "keywords": ["docker image", "my topic"]
}
```
You can specify any fields of a Zenodo deposition, following the specification at https://developers.zenodo.org/#representation.
