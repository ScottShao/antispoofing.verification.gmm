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
  args = parser.parse_args()

  # Loads the configuration 
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = torch.db.replay.Database()

  # Directories containing the features
  import gmm
  for d in os.listdir(config.features_dir):
    
    # Checks that the base directory for storing the gmm statistics exists
    utils.ensure_dir(os.path.join(config.gmmstats_dir,d))

    features_input = db.files(
        directory=os.path.join(config.features_dir,d),
        extension='.hdf5',
        )

    gmmstats_output = db.files(
        directory=os.path.join(config.gmmstats_dir,d),
        extension='.hdf5',
        )

    # Processes the features
    gmm.gmm_stats(features_input, config.ubm_filename, gmmstats_output, 
        args.force)

if __name__ == "__main__": 
  main()
