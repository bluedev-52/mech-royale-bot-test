#!/bin/bash
# usage: sweep.sh name params_json [matches]
cd ~/repos/mech-royale-bot
python3 -m sim.run --bot agent --matches ${3:-96} --jobs 8 --params "$2" --out ~/work/r_$1.json > ~/work/r_$1.txt 2>&1
