
def eval_template(fmt, **env):
    return eval(f'f"{fmt}"', env)

deposition_templates = {
    "upload_type": "other",
    "title": "Docker image {image.name}",
    "version": "{image.tag}",
    "publication_date": "{image.labels.get('org.label-schema.build-date', image.inspect['Created'])[:10]}",
    "keywords": "docker image",
    "description": """TODO""",
}
