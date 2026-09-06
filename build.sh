#!/bin/bash

python build.py
npx antora antora-playbook.yml
touch docs/.nojekyll

