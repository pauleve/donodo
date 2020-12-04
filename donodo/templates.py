
def eval_template(fmt, **env):
    if isinstance(fmt, list):
        return [eval_template(f, **env) for f in fmt]
    if isinstance(fmt, dict):
        return {k: eval_template(v, **env) for k,v in fmt.items()}
    return eval(f'f"{fmt}"', env)

deposition_templates = {
    "upload_type": "other",
    "access_right": "open",
    "license": "cc-by",
    "creators": [{"name": "{image.name.split('/')[0]}"}],
    "title": "Docker image {image.name}",
    "version": "{image.tag}",
    "publication_date": "{image.labels.get('org.label-schema.build-date', image.inspect['Created'])[:10]}",
    "keywords": ["docker image"],
    "description": """TODO""",
}
