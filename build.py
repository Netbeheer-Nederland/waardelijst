import os
import os.path
import json
import textwrap
import shutil
import jinja2
from pyoxigraph import *

NAL_FILE = "src/netbeheerder/netbeheerder.skos.ttl"
ANTORA_COMPONENT_DIR = "_docs-adoc"

# Read and query
nal = Store()
for triple in parse(path=NAL_FILE, format=RdfFormat.TURTLE):
    nal.add(triple)

# Parse query and serialize to dictionary
scheme = json.loads(nal.query('''
    PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT *
    WHERE {
        ?id a skos:ConceptScheme ;
            rdfs:seeAlso ?seeAlso ;
            skos:notation ?name ;
            dcterms:title ?title .
    }
''').serialize(format=QueryResultsFormat.JSON))["results"]["bindings"][0]

print(scheme)

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
            skos:notation ?notation .
    }
 ''').serialize(format=QueryResultsFormat.JSON))["results"]["bindings"], key=lambda t: t["id"]["value"])

# Create Antora component
shutil.rmtree(ANTORA_COMPONENT_DIR)
os.makedirs(ANTORA_COMPONENT_DIR)

## Write component descriptor file
with open(os.path.join(ANTORA_COMPONENT_DIR, "antora.yml"), "wt") as f:
    f.write(textwrap.dedent(f'''
        name: ROOT
        version: ~
    ''').strip())

## Write page
pages_dir = os.path.join(ANTORA_COMPONENT_DIR, "modules", "ROOT", "pages")
os.makedirs(pages_dir, exist_ok=True)

adoc_template = jinja2.Environment(loader=jinja2.FileSystemLoader(".")).get_template("name-authority-list.adoc.jinja2")
adoc = adoc_template.render(scheme=scheme, base_iri="https://modellen.netbeheernederland.nl/name-authority-lists/netbeheerder#", terms=terms)  # TODO: Base IRI should be parsed from document.

with open(os.path.join(pages_dir, scheme["name"]["value"] + ".adoc"), "wt") as f:
    f.write(adoc)
