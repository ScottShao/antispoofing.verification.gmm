#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

import os
import torch


def hist_inter_2D(a, b):
  """Computes the histogram intersection between two arrays of histograms"""
  if a.shape() != b.shape():
    raise RuntimeError, "The two arrays are of different shapes."
  dist = 0
  for i in range(0, a.shape()[0]):
    for j in range(0, a.shape()[1]):
      dist += min(a[i,j], b[i,j])
  return dist


def lgbphs_enrol_model(enrol_files, model_path):
  """Enrols a client model and saves it to the given file"""
  c = 0 # counts the number of enrolment files
  model = torch.core.array.float64_2()
  for k in sorted(enrol_files.keys()):
    # Processes one file
    img = torch.core.array.load( str(enrol_files[k]) )

    if model.extent(0) == 0 or model.extent(1) == 0:
      model.resize(img.extent(0), img.extent(1))
      model.fill(0)
    if img.extent(0) != model.extent(0) or img.extent(1) != model.extent(1):
      raise Exception('Size mismatched')

    model += img.cast('float64')
    c += 1

  # Normalizes the model
  model /= c
  # Saves to file
  model.save(model_path)


def lgbphs_scores(model_file, probe_files):
  """Computes the score of each probe against the model. 
     The measure is the negative Euclidean distance.
     A high score (negative value close) to zero occurs when a probe 
     matches the model"""
  scores = torch.core.array.float64_2((1,len(probe_files)))
  # Loads the model
  if not os.path.exists(model_file):
    raise RuntimeError, "Could not find model %s." % model_file
  model = torch.core.array.load( str(model_file) )
  # Loops over the probes
  i = 0
  for f in probe_files:
    if not os.path.exists(str(f)):
      raise RuntimeError, "Could not find model %s." % str(f)
    probe = torch.core.array.load(str(f))
    scores[0,i] = hist_inter_2D(model,probe)
    i += 1
  # Returns the (negative) distance between the samples and the model
  return scores


def lgbphs_scores_A(models_ids, models_dir, probe_files, db,
                 zt_norm_A_dir, scores_nonorm_dir, group, probes_split_id):
  """Computes a split of the A matrix for the ZT-Norm and saves the raw scores to file"""
  
  # Gets the probe samples
  probe_tests = []
  for k in sorted(probe_files.keys()):
    probe_tests.append(str(probe_files[k][0]))

  # Computes the raw scores for each model
  for model_id in models_ids:
    model_path = os.path.join(models_dir, str(model_id) + ".hdf5")
    A = lgbphs_scores(model_path, probe_tests)
    torch.io.Array(A).save(os.path.join(zt_norm_A_dir, group, str(model_id) + "_" + str(probes_split_id).zfill(4) + ".hdf5"))

    # Saves to text file
    import utils
    scores_list = utils.convertScoreToList(A.as_row(), probe_files)
    sc_nonorm_filename = os.path.join(scores_nonorm_dir, group, str(model_id) + "_" + str(probes_split_id).zfill(4) + ".txt")
    f_nonorm = open(sc_nonorm_filename, 'w')
    for x in scores_list:
      f_nonorm.write(str(x[2]) + " " + str(x[0]) + " " + str(x[3]) + " " + str(x[4]) + "\n")
    f_nonorm.close()


def lgbphs_ztnorm_B(models_ids, models_dir, zfiles, db,
                 zt_norm_B_dir, group, zsamples_split_id):
  """Computes a split of the B matrix for the ZT-Norm"""
  
  # Gets the Z-Norm impostor samples
  zprobe_tests = []
  for k in sorted(zfiles.keys()):
    zprobe_tests.append(str(zfiles[k][0]))

  # Loads the models
  for model_id in models_ids:
    model_path = os.path.join(models_dir, str(model_id) + ".hdf5")
    B = lgbphs_scores(model_path, zprobe_tests)
    torch.io.Array(B).save(os.path.join(zt_norm_B_dir, group, str(model_id) + "_" + str(zsamples_split_id).zfill(4) + ".hdf5"))


def lgbphs_ztnorm_C(tmodel_id, tnorm_models_dir, probe_files, db,
                 zt_norm_C_dir, group, probes_split_id):
  """Computes a split of the C matrix for the ZT-Norm"""

  # Gets the probe samples
  probe_tests = []
  for k in sorted(probe_files.keys()):
    probe_tests.append(str(probe_files[k][0]))

  # Computes the raw scores for the T-Norm model
  model_path = os.path.join(tnorm_models_dir, str(tmodel_id) + ".hdf5")
  C = lgbphs_scores(model_path, probe_tests)
  torch.io.Array(C).save(os.path.join(zt_norm_C_dir, group, "TM" + str(tmodel_id) + "_" + str(probes_split_id).zfill(4) + ".hdf5"))


def lgbphs_ztnorm_D(tnorm_models_ids, tnorm_models_dir, zfiles, db,
                 zt_norm_D_dir, zt_norm_D_sameValue_dir, group, zsamples_split_id):
  """Computes a split of the D matrix for the ZT-Norm"""

  # Gets the Z-Norm impostor samples
  zprobe_tests = []
  znorm_clients_ids = []
  for k in sorted(zfiles.keys()):
    zprobe_tests.append(str(zfiles[k][0]))
    znorm_clients_ids.append(zfiles[k][3])

  # Loads the T-Norm models
  for tmodel_id in tnorm_models_ids:
    tmodel_path = os.path.join(tnorm_models_dir, str(tmodel_id) + ".hdf5")
    D = lgbphs_scores(tmodel_path, zprobe_tests)
    torch.io.Array(D).save(os.path.join(zt_norm_D_dir, group, str(tmodel_id) + "_" + str(zsamples_split_id).zfill(4) + ".hdf5"))

    tnorm_clients_ids = [db.getClientIdFromModelId(tmodel_id)]
    D_sameValue_tm = torch.machine.ztnormSameValue(tnorm_clients_ids, znorm_clients_ids)
    torch.io.Array(D_sameValue_tm).save(os.path.join(zt_norm_D_sameValue_dir, group, str(tmodel_id) + "_" + str(zsamples_split_id).zfill(4) + ".hdf5"))
