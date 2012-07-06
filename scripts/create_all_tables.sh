#!/bin/bash 
# Andre Anjos <andre.anjos@idiap.ch>
# Thu 26 Jan 2012 16:39:07 CET

prefix="replay_perf_table.py --config-file=config/gmm_replay.py"

# Runs all required performance tables
for f in 10 20 50 100 150 200 220; do
  ${prefix} --frames=${f} --thourough #baseline
  ${prefix} --frames=${f} --protocol="print"
  ${prefix} --frames=${f} --protocol="photo"
  ${prefix} --frames=${f} --protocol="video"
  ${prefix} --frames=${f} --protocol="mobile"
  ${prefix} --frames=${f} --protocol="highdef"
  ${prefix} --frames=${f} --protocol="grandtest"
done

exit 0
