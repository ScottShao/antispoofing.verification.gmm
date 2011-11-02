#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os, math


def main():
  import argparse
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

  # Directories containing the images and the annotations
  db = config.db
  img_input = db.files(directory=config.img_input_dir, extension=config.img_input_ext, protocol=config.protocol, **config.all_files_options)
  pos_input = db.files(directory=config.pos_input_dir, extension=config.pos_input_ext, protocol=config.protocol, **config.all_files_options)
  prep_output = db.files(directory=config.features_dir, extension=config.features_ext, protocol=config.protocol, **config.all_files_options)

  # finally, if we are on a grid environment, just find what I have to process.
  import utils
  if args.grid:
    pos = int(os.environ['SGE_TASK_ID']) - 1
    n_total = config.TOTAL_ARRAY_JOBS
    n_per_job = math.ceil(len(img_input) / float(config.TOTAL_ARRAY_JOBS))
    
    if pos >= n_total:
      raise RuntimeError, "Grid request for job %d on a setup with %d jobs" % \
          (pos, n_total)
    img_input_g = utils.split_dictionary(img_input, n_per_job)[pos]
    pos_input_g = utils.split_dictionary(pos_input, n_per_job)[pos]
    img_input = img_input_g
    pos_input = pos_input_g

  # Checks that the base directory for storing the preprocessed images exists
  utils.ensure_dir(config.features_dir)

  import features
  features.tantriggs.compute(img_input, pos_input, prep_output,
    config.CROP_EYES_D, config.CROP_H, config.CROP_W, config.CROP_OH, config.CROP_OW,
    config.GAMMA, config.SIGMA0, config.SIGMA1, config.SIZE, config.THRESHOLD, config.ALPHA,
    config.first_annot, args.force)

if __name__ == "__main__": 
  main()
