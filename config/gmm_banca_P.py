#!/usr/bin/env python

import os
import torch

N_MAX_FILES_PER_JOB = 100
N_MAX_PROBES_PER_JOB = 1000

# 0/ The database to use
db = torch.db.banca.Database()
protocol = 'P'
base_output_dir = "/idiap/temp/lelshafey/banca/gmm"

# 1/ Face normalization
img_input_dir = "/idiap/group/vision/visidiap/databases/banca/english/images_gray"
img_input_ext = ".pgm"
pos_input_dir = "/idiap/group/vision/visidiap/databases/groundtruth/banca/english/eyecenter"
pos_input_ext = ".pos"
features_dir = os.path.join(base_output_dir, "features")
features_ext = ".hdf5"
first_annot = 0
all_files_options = {}

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
BLOCK_H = 12
BLOCK_W = 12
OVERLAP_H = 11
OVERLAP_W = 11
N_DCT_COEF = 45


# 2/ UBM
ubm_filename = os.path.join(base_output_dir, "ubm.hdf5")
gmmstats_dir = os.path.join(base_output_dir, "gmmstats")
gmmstats_ext = ".hdf5"
world_options = { 'subworld': "twothirds" }
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
tnorm_models_dir = os.path.join(base_output_dir, protocol, "tnorm_models")
iterg_enrol = 1
convergence_threshold = 0.0005
variance_threshold = 0.0005
relevance_factor = 4
responsibilities_threshold = 0

models_dir = os.path.join(base_output_dir, protocol, "models")

linear_scoring = True
zt_norm = True

zt_norm_A_dir = os.path.join(base_output_dir, protocol, "zt_norm_A")
zt_norm_B_dir = os.path.join(base_output_dir, protocol, "zt_norm_B")
zt_norm_C_dir = os.path.join(base_output_dir, protocol, "zt_norm_C")
zt_norm_D_dir = os.path.join(base_output_dir, protocol, "zt_norm_D")
zt_norm_D_sameValue_dir = os.path.join(base_output_dir, protocol, "zt_norm_D_sameValue")

scores_nonorm_dir = os.path.join(base_output_dir, protocol, "scores", "nonorm")
scores_ztnorm_dir = os.path.join(base_output_dir, protocol, "scores", "ztnorm")
