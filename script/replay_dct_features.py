#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.dos.anjos@gmail.com>
# Mon 31 Oct 15:06:31 2011 

"""Calculates the features for all input enrollment videos in the replay attack
database. We calculate features for every 10th frame in the video input.
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
  parser.add_argument('-f', '--force', dest='force', action='store_true',
      default=False, help='Force to erase former data if already exists')
  args = parser.parse_args()

  # Loads the configuration 
  import imp 
  config = imp.load_source('config', args.config_file)

  # Imports the feature calculation from LES/CMC
  import features
  import faceloc

  # Directories containing the images and the annotations
  db = torch.db.replay.Database()
  files = db.files(cls=('real', 'attack', 'enroll'), 
      directory=config.video_input_dir, extension='.mov')

  for index, key in enumerate(sorted(files.keys())):
    print "Processing file %d (%d/%d)..." % (key, index+1, len(files))
    
    # bootstraps video reader for client
    video = torch.io.VideoReader(files[key])

    # loads face locations - roll localization
    stem = db.paths([key])[0]
    flocfile = os.path.expanduser(os.path.join(config.pos_input_dir,
      stem)) + '.face'
    locations = faceloc.read_face(flocfile)
    locations = faceloc.expand_detections(locations, video.numberOfFrames)

    for frame_index, frame in enumerate(video):

      if (frame_index+1) % 10: continue
      output_dir = os.path.join(config.features_dir, '%03d' % (frame_index+1))
      output_filename = os.path.join(output_dir, stem) + '.hdf5'

      if frame_index >= len(locations) or not locations[frame_index] or \
          not locations[frame_index].is_valid():
        print "Skipping frame %d of file %s: no face detected" % \
            (frame_index, files[key])
        continue

      # if we continue, there was a detected face for the present frame
      anthropo = faceloc.Anthropometry19x19(locations[frame_index])

      if not os.path.exists(os.path.dirname(output_filename)):
        os.makedirs(os.path.dirname(output_filename))

      # some house-keeping commands
      if os.path.exists(output_filename):
        if args.force:
          print "Backing-up existing feature file %s..." % output_filename
          if os.path.exists(output_filename + '~'): 
            os.unlink(output_filename + '~')
          os.rename(output_filename, output_filename + '~')
        else:
          raise RuntimeError, "output file path %s already exists and you did not --force" % output_filename

      # finally, computes the features for this particular frame
      features.dct.compute_loaded_replay(frame, 
          anthropo.eye_centers(), 
          output_filename,
          config.CROP_EYES_D, 
          config.CROP_H,
          config.CROP_W,
          config.CROP_OH,
          config.CROP_OW, 
          config.GAMMA, 
          config.SIGMA0,
          config.SIGMA1,
          config.SIZE,
          config.THRESHOLD, 
          config.ALPHA, 
          config.BLOCK_H,
          config.BLOCK_W, 
          config.OVERLAP_H,
          config.OVERLAP_W,
          config.N_DCT_COEF)

if __name__ == '__main__':
  main()
