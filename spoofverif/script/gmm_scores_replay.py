#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
import sys
import bob
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
  db = bob.db.replay.Database()

  # (sorted) list of models
  print "Querying database for model names...",
  sys.stdout.flush()
  enroll_list = db.files(cls='enroll', groups=('devel', 'test'))
  client_list = set()
  for key, value in enroll_list.iteritems():
    client_id = value.split('_')[0].split('/')[1]
    client_list.add(client_id)
  client_list = sorted(list(client_list))
  print "%d models" % len(client_list)

  # List of probes
  print "Listing files to be probed...",
  sys.stdout.flush()
  L = db.files(cls=('attack','real'), groups=('devel', 'test')).values()
  files = []
  for d in os.listdir(config.gmmstats_dir):
    files += [os.path.join(d,k) for k in L \
        if os.path.exists(os.path.join(config.gmmstats_dir, d , k + '.hdf5'))]
  print "%d probes" % len(files)
 
  # This is the fixed list of input files.
  print "Setting up input file list...",
  sys.stdout.flush()
  input_files = [os.path.join(config.gmmstats_dir, k + '.hdf5') for k in files]
  print "done"

  # finally, if we are on a grid environment, just find what I have to process.
  if args.grid:
    print "Setting-up grid execution for task id = %s..." % (os.environ['SGE_TASK_ID']),
    pos = int(os.environ['SGE_TASK_ID']) - 1
    if pos >= len(client_list):
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, len(client_list))
    client_list = [client_list[pos]] # gets the right key
    print "done"

  # loops over the model ids and compute scores
  import gmm
  for model_id in client_list:

    # Results go arranged by model id:
    base_output_dir = os.path.join(config.scores_dir, model_id)

    # Checks that the base directories for storing the scores exist
    utils.ensure_dir(base_output_dir)

    # Creates temporary lists for the input and output
    output_files = [os.path.join(base_output_dir, k + '.hdf5') for k in files]

    # Computes the raw scores (i.e. ZT-Norm A matrix or a split of it)
    model_filename = os.path.join(config.models_dir, model_id + '.hdf5')

    print "Running analysis for model %s (%s)..." % (model_id, model_filename)

    gmm.gmm_scores_replay(model_filename, input_files, output_files,
        config.ubm_filename)

if __name__ == "__main__": 
  main()
