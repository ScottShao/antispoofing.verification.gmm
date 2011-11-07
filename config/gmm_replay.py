#!/usr/bin/env python

import os
import torch

# 0/ The database to use
#base_output_dir = "results"
base_output_dir = "/idiap/temp/aanjos/spoofing/verif"

# 1/ Face normalization
#video_input_dir = '/Users/andre/work/replay/protocols'
video_input_dir = '/idiap/group/replay/database/protocols'
pos_input_dir = os.path.join(video_input_dir, 'keylemon-face-locations')
features_dir = os.path.join(base_output_dir, "features")
every_n_frames = 10 #means: take 1 in every N frames

# Cropping
CROP_EYES_D = 33
CROP_H = 80
CROP_W = 64
CROP_OH = 16
CROP_OW = 32

# Tan Triggs
GAMMA = 0.2
SIGMA0 = 1.
SIGMA1 = 2.
SIZE = 5
THRESHOLD = 10.
ALPHA = 0.1

# DCT blocks
BLOCK_H = 8
BLOCK_W = 8
OVERLAP_H = 7
OVERLAP_W = 7
N_DCT_COEF = 28

# 2/ UBM
frames_to_use = 375 #use up to frame #375
ubm_filename = os.path.join(base_output_dir, "ubm.hdf5")
gmmstats_dir = os.path.join(base_output_dir, "gmmstats")
nb_gaussians = 512
iterk = 500
iterg_train = 500
end_acc = 0.0005
var_thd = 0.0005
update_weights = True
update_means = True
update_variances = True
norm_KMeans = True

# 3/ GMM
tnorm_models_dir = os.path.join(base_output_dir, "tnorm_models")
iterg_enrol = 1
convergence_threshold = 0.0005
variance_threshold = 0.0005
relevance_factor = 4
responsibilities_threshold = 0

models_dir = os.path.join(base_output_dir, "models")
scores_dir = os.path.join(base_output_dir, "scores")

linear_scoring = True
zt_norm = False
