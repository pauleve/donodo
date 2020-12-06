
import json

def eval_template(fmt, **env):
    if isinstance(fmt, list):
        return [eval_template(f, **env) for f in fmt]
    if isinstance(fmt, dict):
        return {k: eval_template(v, **env) for k,v in fmt.items()}
    return eval(f'f"""{fmt}"""', env)

deposition_templates = {
    "upload_type": "other",
    "access_right": "open",
    "license": "cc-by",
    "creators": [{"name": "{image.name.split('/')[0]}"}],
    "title": "Docker image {image.name}",
    "version": "{image.tag}",
    "publication_date": "{image.labels.get('org.label-schema.build-date', image.inspect['Created'])[:10]}",
    "keywords": ["docker image"],
    "description": """<p>This record contains an exportation of the Docker image
    <strong>{image.name}:{image.tag}</strong>.</p>
    <p>The image can be imported using the command <code>docker load</code> with
    the image file:</p>
<pre>
<code>docker load -i image.tar.gz</code></pre>

<p>or with the <code>donodo</code> command  available at <a
href="https://github.com/pauleve/donodo">https://github.com/pauleve/donodo</a>:</p>
<pre>
<code>pip install -U donodo
donodo pull [DOI]</code></pre>

""",
}

def custom_templates_from_json(jsonfile):
    with open(jsonfile) as fp:
        user_templates = json.load(fp)
    deposition_templates.update(user_templates)
