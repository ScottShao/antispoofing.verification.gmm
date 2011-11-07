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
  db = torch.db.replay.Database()

  # Run for attacks and real-accesses for the development and test groups
  process = db.files(cls=('attack','real'), groups=('devel', 'test'))

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    ordered_keys = sorted(process.keys())
    if pos >= len(ordered_keys):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(ordered_keys))
    key = ordered_keys[pos] # gets the right key
    process = {key: process[key]}

  # Directories containing the features
  features_input = []
  gmmstats_output = []
  for d in os.listdir(config.features_dir):
    for key, value in process.iteritems():
      features_input.append(os.path.join(config.features_dir, d, value + '.hdf5'))
      gmmstats_output.append(os.path.join(config.gmmstats_dir, d, value + '.hdf5'))

  import gmm

  gmm.gmm_stats(dict(enumerate(features_input)), 
      config.ubm_filename, dict(enumerate(gmmstats_output)), args.force)

if __name__ == "__main__": 
  main()
