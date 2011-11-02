#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
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
  db = config.db

  for group in ['dev', 'eval']:
    # (sorted) list of models
    models_ids = sorted(db.models(protocol=config.protocol, groups=group))

    # Checks that the base directory for storing the ZT-norm scores exists
    utils.ensure_dir(os.path.join(config.scores_ztnorm_dir, group))

    # Loops over the model ids
    for model_id in models_ids:
      # Loads probe files to get information about the type of access
      probe_files = db.objects(groups=group, protocol=config.protocol, purposes="probe", model_ids=(model_id,))

      # Loads A, B, C, D and D_sameValue matrices
      A = torch.core.array.load(os.path.join(config.zt_norm_A_dir, group, str(model_id) + ".hdf5"))
      B = torch.core.array.load(os.path.join(config.zt_norm_B_dir, group, str(model_id) + ".hdf5"))
      C = torch.core.array.load(os.path.join(config.zt_norm_C_dir, group, str(model_id) + ".hdf5"))
      D = torch.core.array.load(os.path.join(config.zt_norm_D_dir, group, "D.hdf5"))
      D_sameValue = torch.core.array.load(os.path.join(config.zt_norm_D_sameValue_dir, group, "D_sameValue.hdf5")).cast('bool')
      ztscores_m = torch.machine.ztnorm(A, B, C, D, D_sameValue)

      # Saves to text file
      ztscores_list = utils.convertScoreToList(ztscores_m.as_row(), probe_files)
      sc_ztnorm_filename = os.path.join(config.scores_ztnorm_dir, group, str(model_id) + ".txt")
      f_ztnorm = open(sc_ztnorm_filename, 'w')
      for x in ztscores_list:
        f_ztnorm.write(str(x[2]) + " " + str(x[0]) + " " + str(x[3]) + " " + str(x[4]) + "\n")
      f_ztnorm.close()

if __name__ == "__main__": 
  main()
