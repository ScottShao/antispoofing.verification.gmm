#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os, sys
import torch
import utils
import argparse

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-g', '--group', metavar='STR', type=str,
      dest='group', default="", help='Database group (\'dev\' or \'eval\') for which to retrieve T-norm models.')
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config_file', default="", help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')
  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exist')
  parser.add_argument('--grid', dest='grid', action='store_true',
      default=False, help='If set, assumes it is being run using a parametric grid job. It orders all ids to be processed and picks the one at the position given by ${SGE_TASK_ID}-1')
  args = parser.parse_args()

  # Loads the configuration 
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = config.db
  # (sorted) list of T-norm models
  tmodels_ids = sorted(db.Tmodels(protocol=config.protocol, groups=args.group))

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(tmodels_ids):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(tmodels_ids))
    tmodels_ids = [tmodels_ids[pos]]

  # Checks that the base directory for storing the T-Norm models exists
  utils.ensure_dir(config.tnorm_models_dir)

  # Trains the T-Norm models
  import pca
  for tmodel_id in tmodels_ids:
    # Path to the T-Norm model
    tmodel_path = os.path.join(config.tnorm_models_dir, str(tmodel_id) + ".hdf5")

    # Removes old file if required
    if args.force and os.path.exists(tmodel_path):
      print "Removing old PCA T-Norm model"
      os.remove(tmodel_path)

    if os.path.exists(tmodel_path):
      print "T-Norm model %s already exists." % tmodel_path
    else:
      print "Enroling T-Norm model %s." % tmodel_path
      enrol_files = db.Tfiles(directory=config.featuresProjected_dir, extension=config.featuresProjected_ext, 
                              groups=args.group, protocol=config.protocol, model_ids=(tmodel_id,))
      pca.pca_enrol_model(enrol_files, tmodel_path)

if __name__ == "__main__": 
  main()
