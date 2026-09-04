#!/bin/env bash

set -e

DOCS_ADOC_DIR=_docs-adoc
rm -rf $DOCS_ADOC_DIR
mkdir -p $DOCS_ADOC_DIR
COMPONENT_DESCRIPTOR=$DOCS_ADOC_DIR/modules/ROOT
ROOT_MODULE=$DOCS_ADOC_DIR/antora.yml

for waardelijst_path in src/*; do
    waardelijst=$(basename ${waardelijst_path%.ttl})
    jinja2 -o $ROOT_MODULE/pages/$waardelijst.adoc codelist.adoc.jinja2 $linkml

    cp -r $src_dir $DOCS_ADOC_DIR/
    root_module=docs-adoc/$version/modules/ROOT
    linkml=$src_dir/modules/ROOT/attachments/schema/prof_ap_cim.linkml.yml
    jinja2 -o $root_module/partials/preamble.adoc $src_dir/modules/ROOT/partials/preamble.adoc $linkml
    jinja2 -o $root_module/partials/metadata.adoc $src_dir/modules/ROOT/partials/metadata.adoc $linkml
    jinja2 -o $root_module/partials/header.adoc $src_dir/modules/ROOT/partials/header.adoc $linkml
    jinja2 -o $root_module/partials/schema-diagram.d2 $src_dir/modules/ROOT/partials/schema-diagram.d2 $linkml
    jinja2 -o $root_module/partials/schema-classes.adoc $src_dir/modules/ROOT/partials/schema-classes.adoc $linkml
    jinja2 -o $root_module/partials/schema-namespaces.adoc $src_dir/modules/ROOT/partials/schema-namespaces.adoc $linkml
    jinja2 -o $root_module/pages/index.adoc $src_dir/modules/ROOT/pages/index.adoc $linkml

    linkml=$src_dir/schema/prof_ap_cim.linkml.yml

    mkdir -p $root_module/{attachments,images,pages}
    mkdir $root_module/attachments/examples

    echo "name: ROOT" >> $root_module/../../antora.yml
    echo "version: '$(yq .version $linkml)'" >> $root_module/../../antora.yml
    echo "title: $(yq .title $linkml)" >> $root_module/../../antora.yml

    jinja2 -o $root_module/pages/index.adoc $src_dir/prof_ap_cim.adoc $linkml

    cp \
        $linkml \
        $src_dir/schema/prof_ap_cim.shacl.ttl \
        $src_dir/schema/prof_ap_cim.context.jsonld \
    $root_module/attachments

    cp \
        $linkml \
        $src_dir/examples/diagram_layout_ap.yml \
        $src_dir/examples/diagram_layout_ap.jsonld \
    $root_module/attachments/examples
done

npx antora ${1:-antora-playbook.yml}
touch docs/.nojekyll
# TODO: Consider copying some artifacts files here (SHACL, JSON-LD context) so you can get cleaner URIs for them.
