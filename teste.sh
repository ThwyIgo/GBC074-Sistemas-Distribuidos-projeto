#!/usr/bin/env sh
. ./compile.sh source
python_venv

# Portas
# 40XX - bases de dados (hard-coded)
#     400X - cluster 0 de bases de dados
#     401X - cluster 1 de bases de dados
# 41XX - bib-server
# 42XX - cad-server

trap "exit" INT TERM
trap "kill 0" EXIT

db-server 0 0 &
db-server 1 0 &
db-server 2 0 &
db-server 0 1 &
db-server 1 1 &
db-server 2 1 &
sleep 1
bib-server 4142 4000 4010 &
bib-server 4143 4002 4012 &
cad-server 4242 4000 4010 &
cad-server 4243 4001 4001 &

for job in $(jobs -p); do
    wait $job
done