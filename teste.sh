#!/usr/bin/env sh
. ./compile.sh source
python_venv

trap "exit" INT TERM
trap "kill 0" EXIT

db-server 0 0 &
db-server 1 0 &
db-server 2 0 &
bib-server 4142 4000 &
bib-server 4143 4002 &
cad-server 4242 4000 &
cad-server 4243 4001 &

for job in $(jobs -p); do
    wait $job
done