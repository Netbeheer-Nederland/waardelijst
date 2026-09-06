import json
import jinja2
from pyoxigraph import *

# Read and query
nal = Store()
for triple in parse(path="src/netbeheerder/netbeheerder.skos.ttl", format=RdfFormat.TURTLE):
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
            skos:notation ?notation ;
            skos:topConceptOf ?scheme .
        ?scheme dcterms:title ?schemeTitle .
    }
 ''').serialize(format=QueryResultsFormat.JSON))["results"]["bindings"], key=lambda t: t["id"]["value"])

# Render AsciiDoc page
adoc_template = jinja2.Environment(loader=jinja2.FileSystemLoader(".")).get_template("name-authority-list.adoc.jinja2")
adoc = adoc_template.render(scheme=scheme, terms=terms)
print(adoc)
