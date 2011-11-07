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
  parser.add_argument('--grid', dest='grid', action='store_true',
      default=False, help='If set, assumes it is being run using a parametric grid job. It orders all ids to be processed and picks the one at the position given by ${SGE_TASK_ID}-1')
  args = parser.parse_args()

  # Loads the configuration
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = torch.db.replay.Database()

  # (sorted) list of models
  enroll_list = db.files(cls='enroll')
  client_list = set()
  for key, value in enroll_list():
    client_id = value.split('_')[0].split('/')[1]
    client_list.add(client_id)
  client_list = sorted(list(client_list))

  # List of probes
  probe_dict = db.files(protocol='print',
      directory=config.accumulated_gmmstats_dir,
      extension='.hdf5')
  probe_stem = db.files(protocol='print')

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(client_list):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(client_list))
    cilent_list = [client_list[pos]] # gets the right key

  # loops over the model ids and compute scores
  import gmm
  for model_id in client_list:
    
    # Results go arranged by model id:
    base_output_dir = os.path.join(config.scores_dir, model_id)

    # Checks that the base directories for storing the scores exist
    utils.ensure_dir(base_output_dir)

    # Computes the raw scores (i.e. ZT-Norm A matrix or a split of it)
    model_filename = os.path.join(config.models_dir, model_id + '.hdf5')
    gmm.gmm_scores_replay(model_filename,
        probe_dict, probe_stem,
        config.ubm_filename, 
        base_output_dir)

if __name__ == "__main__": 
  main()
