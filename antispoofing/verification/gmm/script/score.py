#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
import sys

def main():

  import argparse

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)

  parser.add_argument('stats', metavar='DIR', type=str, help='Root directory containing the UBM statistics for the Replay-Attack database')
 
  parser.add_argument('ubm', metavar='FILE', type=str, help='The trained UBM')
  
  parser.add_argument('models', metavar='DIR', type=str, help='Root directory containing the models for the Replay-Attack database')
 
  parser.add_argument('outputdir', metavar='DIR', type=str, help='Directory where the scores will be saved at')
  
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str, dest='config', default=None, help='Filename of the configuration file with parameters for feature extraction and verification (defaults to loading what is in the module "antispoofing.verification.gmm.config.gmm_replay")')

  parser.add_argument('--grid', dest='grid', action='store_true',
      default=False, help=argparse.SUPPRESS)

  from ..version import __version__
  name = os.path.basename(os.path.splitext(sys.argv[0])[0])
  parser.add_argument('-V', '--version', action='version',
      version='PB-GMM for ReplayAttack Database v%s (%s)' % (__version__, name))
  
  args = parser.parse_args()

  # Loads the configuration 
  if args.config is None:
    import antispoofing.verification.gmm.config.gmm_replay as config
  else:
    import imp
    config = imp.load_source('config', args.config)

  # Database
  import bob
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
  for d in os.listdir(args.stats):
    files += [os.path.join(d,k) for k in L \
        if os.path.exists(os.path.join(args.stats, d , k + '.hdf5'))]
  print "%d probes" % len(files)
 
  # This is the fixed list of input files.
  print "Setting up input file list...",
  sys.stdout.flush()
  input_files = [os.path.join(args.stats, k + '.hdf5') for k in files]
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
  from .. import score
  for model_id in client_list:

    # Results go arranged by model id:
    base_output_dir = os.path.join(args.outputdir, model_id)

    # Checks that the base directories for storing the scores exist
    from ...utils import ensure_dir
    ensure_dir(base_output_dir)

    # Creates temporary lists for the input and output
    output_files = [os.path.join(base_output_dir, k + '.hdf5') for k in files]

    # Computes the raw scores (i.e. ZT-Norm A matrix or a split of it)
    model_filename = os.path.join(args.models, model_id + '.hdf5')

    print "Running analysis for model %s (%s)..." % (model_id, model_filename)
    score(model_filename, input_files, output_files, args.ubm)

if __name__ == "__main__": 
  main()
