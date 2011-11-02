#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os, math
import torch
import utils

import argparse

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-g', '--group', metavar='STR', type=str,
      dest='group', default="", help='Database group (\'dev\' or \'eval\') for which to retrieve models.')
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config_file', default="", help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')
  parser.add_argument('--grid', dest='grid', action='store_true',
      default=False, help='If set, assumes it is being run using a parametric grid job. It orders all ids to be processed and picks the one at the position given by ${SGE_TASK_ID}-1')
  args = parser.parse_args()

  # Loads the configuration 
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = config.db
  # (sorted) list of models
  models_ids = sorted(db.models(protocol=config.protocol, groups=args.group))
  # (sorted) list of T-Norm models
  tmodels_ids = sorted(db.Tmodels(protocol=config.protocol, groups=args.group))

  # finally, if we are on a grid environment, just find what I have to process.
  probes_split_id = 0
  if args.grid:
    n_splits = 0
    found = False
    pos = int(os.environ['SGE_TASK_ID']) - 1
    n_probes = len(db.files(protocol=config.protocol, purposes='probe', groups=args.group))
    n_splits = int(math.ceil(n_probes / float(config.N_MAX_PROBES_PER_JOB)))
    if pos < n_splits * len(tmodels_ids):
      tmodels_ids = [tmodels_ids[pos / n_splits]]
      probes_split_id = pos % n_splits
      found = True
    if found == False:
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, n_splits)

  # Loops over the model ids
  for model_id in models_ids:
    # Checks that the base directories for storing the ZT-norm C matrix exist
    utils.ensure_dir(os.path.join(config.zt_norm_C_dir, args.group))

  # Gets the probe sample list
  probe_files = db.objects(directory=config.features_dir, extension=config.features_ext, groups=(args.group,), protocol=config.protocol, purposes="probe")
    
  # If we are on a grid environment, just keep the required split of Z-norm impostor samples
  if args.grid:
    probe_files_g = utils.split_dictionary(probe_files, config.N_MAX_PROBES_PER_JOB)
    probe_files = probe_files_g[probes_split_id]

  # Computes the ZT-Norm C matrix or a split of it, for the given model
  import lgbphs
  for tmodel_id in tmodels_ids:
    lgbphs.lgbphs_ztnorm_C(tmodel_id, config.tnorm_models_dir, probe_files, db, 
            config.zt_norm_C_dir, args.group, probes_split_id)

if __name__ == "__main__": 
  main()
