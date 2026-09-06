import os
import os.path
import json
import textwrap
import shutil
import jinja2
from pyoxigraph import *

NAL_FILES_DIR = "src"
ANTORA_COMPONENT_DIR = "_docs-adoc"

# Create Antora component
shutil.rmtree(ANTORA_COMPONENT_DIR)
os.makedirs(ANTORA_COMPONENT_DIR)

attachments_dir = os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "attachments")
pages_dir = os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "pages")
os.makedirs(pages_dir, exist_ok=True)
os.makedirs(attachments_dir, exist_ok=True)

## Copy index page
shutil.copyfile(os.path.join(NAL_FILES_DIR, "index.adoc"), os.path.join(pages_dir, "index.adoc"))

## Create nav
with open(os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "nav.adoc"), "wt") as f:
    f.write('')

## Write component descriptor file
with open(os.path.join(ANTORA_COMPONENT_DIR, "antora.yml"), "wt") as f:
    f.write(textwrap.dedent(f'''
        name: ROOT
        title: NBNL Name Authority Lists
        version: ~
        nav:
        - modules/ROOT/nav.adoc
    ''').strip())

for nal_file in os.listdir(NAL_FILES_DIR):
    if nal_file == "index.adoc":
        continue

    nal_file_path = os.path.join(NAL_FILES_DIR, nal_file)
    # Read and query
    nal = Store()
    for triple in parse(path=nal_file_path, format=RdfFormat.TURTLE):
        nal.add(triple)

    # Parse query and serialize to dictionary
    scheme = json.loads(nal.query('''
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE {
            ?id a skos:ConceptScheme ;
                dcterms:subject ?subject ;
                skos:notation ?name ;
                dcterms:title ?title .
        }
    ''').serialize(format=QueryResultsFormat.JSON))["results"]["bindings"][0]

    terms = sorted(json.loads(nal.query('''
        PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX dcterms: <http://purl.org/dc/terms/>
        PREFIX adms: <http://www.w3.org/ns/adms#>
        SELECT *
        WHERE {
            ?id a skos:Concept ;
                skos:prefLabel ?prefLabel ;
                foaf:homepage ?homepage ;
                adms:status ?status ;
                skos:notation ?code .
        }
     ''').serialize(format=QueryResultsFormat.JSON))["results"]["bindings"], key=lambda t: t["id"]["value"])

    # Generate documentation
    adoc_template = jinja2.Environment(loader=jinja2.FileSystemLoader(".")).get_template("name-authority-list.adoc.jinja2")
    adoc = adoc_template.render(scheme=scheme, terms=terms)

    with open(os.path.join(pages_dir, scheme["name"]["value"] + ".adoc"), "wt") as f:
        f.write(adoc)

    # Generate SHACL
    shacl_template = jinja2.Environment(loader=jinja2.FileSystemLoader(".")).get_template("name-authority-list.shacl.ttl.jinja2")
    shacl = shacl_template.render(scheme=scheme, terms=terms)

    with open(os.path.join(attachments_dir, scheme["name"]["value"] + ".shacl.ttl"), "wt") as f:
        f.write(shacl)

    # Copy SKOS file
    shutil.copy(nal_file_path, os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "attachments"))

    # Expand nav
    with open(os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "nav.adoc"), "a") as f:
        f.write(f'* xref::{scheme["name"]["value"]}.adoc[]\n')
