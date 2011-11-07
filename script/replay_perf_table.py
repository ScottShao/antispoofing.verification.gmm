#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 07 Nov 2011 17:55:05 CET 

"""Generates face-verification-like performance tables that can be fed to
performance computation scripts. Two tables are always generated: development
and test.
"""

import sys
import os
import argparse
import torch

def main():

  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config_file', default="", help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')
  parser.add_argument('-p', '--protocol', metavar='PROTOCOL', type=str,
      dest='protocol', default='', help='The name of the protocol to use when evaluating the performance of the data on face verification (defaults to "%(default)s)". If you do *not* specify a protocol, just run the baseline face verification.')
  parser.add_argument('-f', '--frames', metavar='INT', type=int,
      dest='frames', default=15, help='Number of frames to average the scores from')
  parser.add_argument('-i', '--input-dir', metavar='DIR', type=str,
      dest='idir', default='/idiap/temp/aanjos/spoofing/verif/scores',
      help='Name of the directory containing the scores organized in this way: <client-name>/<frame-number>/rcd...')
  args = parser.parse_args()

  # Loads the configuration
  import imp 
  config = imp.load_source('config', args.config_file)

  # Database
  db = torch.db.replay.Database()

  # Finds the files that belong to the negative and positive samples of each
  # of the experiment groups: devel, test
  print "Querying database for model names...",
  sys.stdout.flush()
  client_dict = db.files(cls='enroll', groups=('devel'))
  dev_client = set()
  for key, value in client_dict.iteritems():
    client_id = value.split('_')[0].split('/')[1]
    dev_client.add(client_id)
  dev_client = sorted(list(dev_client))
  client_dict = db.files(cls='enroll', groups=('test'))
  test_client = set()
  for key, value in client_dict.iteritems():
    client_id = value.split('_')[0].split('/')[1]
    test_client.add(client_id)
  test_client = sorted(list(test_client))
  print "%d development;" % len(dev_client),
  print "%d test" % len(test_client)

  # Finds all files for real access
  print "Querying database for real/devel files...",
  sys.stdout.flush()
  dev_real_dict = db.files(cls='real', groups=('devel'))
  print "%d files" % (len(dev_real_dict))

  print "Querying database for real/test files...",
  sys.stdout.flush()
  test_real_dict = db.files(cls='real', groups=('test'))
  print "%d files" % (len(test_real_dict))

  for client_id in dev_client:
    
    positive = [k for k in dev_real_dict.values() if k.find(client_id) >= 0]
    negative = [k for k in dev_real_dict.values() if k.find(client_id) == -1]



    for d in os.listdir(config.scores_dir

if __name__ == '__main__':
  main()
