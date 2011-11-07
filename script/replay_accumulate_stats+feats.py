#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 02 Nov 2011 16:35:54 CET 

"""Accumulate UBM statistics for a certain number of frames.
"""

import os, math
import torch
import utils

import argparse

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config_file', default="", help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')
  args = parser.parse_args()

  # Loads the configuration 
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = torch.db.replay.Database()

  files = db.files()

  use_dirs = []
  for d in os.listdir(config.features_dir):
    if int(d) > config.accumulate_frames:
      print "Ignoring data from directory '%s' -- beyond frame threshold" % d
      continue
    use_dirs.append(d)
    
  for key, stem in files.iteritems():

    # vertical stack features
    output_file = os.path.join(config.acc_features_dir, "up-to-%d" %
      config.accumulate_frames, stem + '.hdf5')
    if os.path.exists(output_file):
      print "Not re-running for existing file %s" % output_file
      continue

    print "Concatenating %d arrays for stem %s" % (len(use_dirs), stem)
    arrays = []
    for frame_no in use_dirs:
      array_file = os.path.join(config.features_dir, frame_no, stem + '.hdf5')
      
      if not os.path.exists(array_file):
        print "Cannot find file %s - skipping" % array_file
        continue

      arrays.append(torch.core.array.load(os.path.join(config.features_dir,
        frame_no, stem + '.hdf5')))
    # stack the arrays into one gigantic array and write to file.
    cated = torch.core.array.cat(arrays, 0)
    utils.ensure_dir(os.path.dirname(output_file))
    print "Saving %d arrays at %s" % (len(use_dirs), output_file)
    cated.save(output_file)

    # accumulate statistics
    print "Accumulating %d statistics for stem %s" % (len(use_dirs), stem)
    T = None
    log_liklihood = None
    n = None
    n_gaussians = None
    n_inputs = None
    sumPx = None
    sumPxx = None
    for frame_no in use_dirs:

      hdf5_path = os.path.join(config.gmmstats_dir, frame_no, stem + '.hdf5')
      if not os.path.exists(hdf5_path):
        print "Cannot find file %s - skipping" % hdf5_path
        continue

      h5f = torch.io.HDF5File(os.path.join(config.gmmstats_dir,
        frame_no, stem + '.hdf5'), 'r')
      if T is None:
        T = h5f.read('T')
        log_liklihood = h5f.read('log_liklihood')
        n = h5f.read('n')
        n_gaussians = h5f.read('n_gaussians')
        n_inputs = h5f.read('n_inputs')
        sumPx = h5f.read('sumPx')
        sumPxx = h5f.read('sumPxx')
      else: 
        T += h5f.read('T')
        log_liklihood += h5f.read('log_liklihood')
        n += h5f.read('n')
        sumPx += h5f.read('sumPx')
        sumPxx += h5f.read('sumPxx')

    output_file = os.path.join(config.acc_gmmstats_dir, "up-to-%d" %
      config.accumulate_frames, stem + '.hdf5')
    utils.ensure_dir(os.path.dirname(output_file))
    print "Saving accumulated statistics at %s" % (output_file)
    h5out = torch.io.HDF5File(output_file, 'w')
    h5out.set('T', T)
    h5out.set('log_liklihood', log_liklihood)
    h5out.set('n', n)
    h5out.set('n_gaussians', n_gaussians)
    h5out.set('n_inputs', n_inputs)
    h5out.set('sumPx', sumPx)
    h5out.set('sumPxx', sumPxx)
    
if __name__ == "__main__": 
  main()
