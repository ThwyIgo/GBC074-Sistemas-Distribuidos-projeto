#!/usr/bin/env sh
. ./compile.sh source

python_venv
cad-server $@