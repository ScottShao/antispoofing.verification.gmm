#!/usr/bin/env python
# Laurent El Shafey <Laurent.El-Shafey@idiap.ch>

"""Submits all feature creation jobs to the Idiap grid"""

import os, sys, math
import argparse

def checked_directory(base, name):
  """Checks and returns the directory composed of os.path.join(base, name). If
  the directory does not exist, raise a RuntimeError.
  """
  retval = os.path.join(base, name)
  if not os.path.exists(retval):
    raise RuntimeError, "You have not created a link to '%s' at your '%s' installation - you don't have to, but then you need to edit this script to eliminate this error" % (name, base)
  return retval

# Finds myself first
FACEVERIFLIB_DIR = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))

# Defines the gridtk installation root - by default we look at a fixed location
# in the currently detected FACEVERIFLIB_DIR. You can change this and hard-code
# whatever you prefer.
GRIDTK_DIR = checked_directory(FACEVERIFLIB_DIR, 'gridtk')
sys.path.insert(0, GRIDTK_DIR)

# Defines the torch5spro installation root - by default we look at a fixed
# location in the currently detected FACEVERIFLIB_DIR. You can change this and
# hard-code whatever you prefer.
#TORCH_DIR = checked_directory(FACEVERIFLIB_DIR, 'torch')

# Defines the replay attack installation root - by default we look at a fixed
# location in the currently detected FACEVERIFLIB_DIR. You can change this and
# hard-code whatever you prefer.
#REPLAY_DIR = checked_directory(FACEVERIFLIB_DIR, 'replay')

# Defines the face annotations installation root - by default we look at a
# fixed location in the currently detected FACEVERIFLIB_DIR. You can change this
# and hard-code whatever you prefer.
#FACES_DIR = checked_directory(FACEVERIFLIB_DIR, 'faces')

# This is a hard-coded number of array jobs we are targeting, for
# parametric jobs.
#TOTAL_REPLAY_FILES = 1200

# The wrapper is required to bracket the execution environment for the faceveriflib
# scripts:
FACEVERIFLIB_WRAPPER = os.path.join(FACEVERIFLIB_DIR, 'shell.py')

# The environment assures the correct execution of the wrapper and the correct
# location of both the 'facevefilib' and 'torch' packages.
FACEVERIFLIB_WRAPPER_ENVIRONMENT = [
    'FACEVERIFLIB_DIR=%s' % FACEVERIFLIB_DIR
#    'TORCH_DIR=%s' % TORCH_DIR,
    ]

def submit(job_manager, command, dependencies=[], array=None, queue=None, mem_free=None, hostname=None):
  """Submits one job using our specialized shell wrapper. We hard-code certain
  parameters we like to use. You can change general submission parameters
  directly at this method."""
 
  from gridtk.tools import make_python_wrapper, random_logdir
  name = os.path.splitext(os.path.basename(command[0]))[0]
  logdir = os.path.join('logs', random_logdir())

  use_cmd = make_python_wrapper(FACEVERIFLIB_WRAPPER, command)
  return job_manager.submit(use_cmd, deps=dependencies, cwd=True,
      queue=queue, mem_free=mem_free, hostname=hostname, 
      stdout=logdir, stderr=logdir, name=name, array=array, 
      env=FACEVERIFLIB_WRAPPER_ENVIRONMENT)


def main():
  """The main entry point, control here the jobs options and other details"""

  # Parses options
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('-s', '--script-file', metavar='FILE', type=str,
      dest='script_file', default="", help='Filename of the script to run on the grid (defaults to "%(default)s")')
  parser.add_argument('-c', '--config-file', metavar='FILE', type=str,
      dest='config_file', default="", help='Filename of the configuration file to use to run the script on the grid (defaults to "%(default)s")')
  args = parser.parse_args()

  # Loads the configuration 
  import imp
  config = imp.load_source('config', args.config_file)
  TOTAL_ARRAY_JOBS = config.TOTAL_ARRAY_JOBS

  # Let's create the job manager
  from gridtk.manager import JobManager
  jm = JobManager()

  # Database
  db = config.db
  
  # Computes T-Norm models if required
  job_tnorm_L = []
  if config.zt_norm:
    for group in ['dev','eval']:
      n_array_jobs = len(db.Tmodels(protocol=config.protocol, groups=(group,)))
      cmd_tnorm = [
                    'lgbphs_tmodels.py',
                    '--group=%s' % group,
                    '--config-file=%s' % args.config_file,
                    '--grid'
                  ]
      job_tnorm_int = submit(jm, cmd_tnorm, dependencies=[], array=(1,n_array_jobs,1))
      job_tnorm_L.append(job_tnorm_int.id())
      print 'submitted:', job_tnorm_int

  # Generates the models 
  job_models_L = []
  for group in ['dev','eval']:
    n_array_jobs = len(db.models(protocol=config.protocol, groups=(group,)))
    cmd_models = [
                  'lgbphs_models.py',
                  '--group=%s' % group,
                  '--config-file=%s' % args.config_file,
                  '--grid'
                  ]
    job_models_int = submit(jm, cmd_models, dependencies=[], array=(1,n_array_jobs,1))
    job_models_L.append(job_models_int.id())
    print 'submitted:', job_models_int

  # Compute scores
  job_scores_A = []
  for group in ['dev','eval']:
    deps = job_models_L
    n_array_jobs = 0
    model_ids = sorted(db.models(protocol=config.protocol, groups=(group,)))
    for model_id in model_ids:
      n_probes_for_model = len(db.files(groups=group, protocol=config.protocol, purposes='probe', model_ids=(model_id,)))
      n_splits_for_model = int(math.ceil(n_probes_for_model / float(config.N_MAX_PROBES_PER_JOB)))
      n_array_jobs += n_splits_for_model
    cmd_models = [
                  'lgbphs_scores_A.py',
                  '--group=%s' % group,
                  '--config-file=%s' % args.config_file,
                  '--grid'
                  ]
    job_scores_int = submit(jm, cmd_models, dependencies=deps, array=(1,n_array_jobs,1), queue='q1d')
    job_scores_A.append(job_scores_int.id())
    print 'submitted:', job_scores_int

  # Merges the raw scores
  job_scores_Am = []
  cmd_scores_Am =  [
                    'scores_A_merge.py',  
                    '--config-file=%s' % args.config_file, 
                    '--grid'
                  ]
  job_scores_Am = submit(jm, cmd_scores_Am, dependencies=job_scores_A) 
  print 'submitted:', job_scores_Am
  

  # Computes the B matrix for ZT-Norm
  job_scores_B = []
  if config.zt_norm:
    for group in ['dev','eval']:
      deps = job_models_L
      # Number of models
      n_model_ids = len(db.models(protocol=config.protocol, groups=(group,)))
      # Number of Z-Norm impostor samples
      n_zsamples = len(db.Zfiles(protocol=config.protocol, groups=group))
      n_zsamples_splits = int(math.ceil(n_zsamples / float(config.N_MAX_PROBES_PER_JOB)))
      # Number of array jobs 
      n_array_jobs = n_model_ids * n_zsamples_splits
      cmd_scores_B = [
                    'lgbphs_scores_B.py',
                    '--group=%s' % group,
                    '--config-file=%s' % args.config_file,
                    '--grid'
                    ]
      job_scores_int = submit(jm, cmd_scores_B, dependencies=deps, array=(1,n_array_jobs,1), queue='q1d')
      job_scores_B.append(job_scores_int.id())
      print 'submitted:', job_scores_int

  # Merges the B matrices 
  job_scores_Bm = []
  cmd_scores_Bm =  [
                    'scores_B_merge.py',  
                    '--config-file=%s' % args.config_file, 
                    '--grid'
                  ]
  job_scores_Bm = submit(jm, cmd_scores_Bm, dependencies=job_scores_B)
  print 'submitted:', job_scores_Bm

 
  # Computes the C matrices for ZT-Norm
  job_scores_C = []
  if config.zt_norm:
    for group in ['dev','eval']:
      deps = job_tnorm_L

      n_array_jobs = 0
      # Number of T-Norm models
      n_tmodels_ids = len(db.Tmodels(protocol=config.protocol, groups=group))
      n_probes = len(db.files(protocol=config.protocol, purposes='probe', groups=group))
      n_splits = int(math.ceil(n_probes / float(config.N_MAX_PROBES_PER_JOB)))
      n_array_jobs = n_splits * n_tmodels_ids

      cmd_scores_C = [
                    'lgbphs_scores_C.py',
                    '--group=%s' % group,
                    '--config-file=%s' % args.config_file,
                    '--grid'
                    ]
      job_scores_int = submit(jm, cmd_scores_C, dependencies=deps, array=(1,n_array_jobs,1), queue='q1d')
      job_scores_C.append(job_scores_int.id())
      print 'submitted:', job_scores_int

  # Merges the C matrices 
  job_scores_Cm = []
  cmd_scores_Cm =  [
                    'scores_C_merge.py',  
                    '--config-file=%s' % args.config_file, 
                    '--grid'
                  ]
  job_scores_Cm = submit(jm, cmd_scores_Cm, dependencies=job_scores_C) 
  print 'submitted:', job_scores_Cm
 

  # Computes the D matrices for ZT-Norm
  job_scores_D = []
  if config.zt_norm:
    for group in ['dev','eval']:
      deps = job_tnorm_L

      # Number of T-Norm models
      n_tnorm_models_ids = len(db.Tmodels(protocol=config.protocol, groups=group))
      # Number of Z-Norm impostor samples
      n_zsamples = len(db.Zfiles(protocol=config.protocol, groups=group))
      n_zsamples_splits = int(math.ceil(n_zsamples / float(config.N_MAX_PROBES_PER_JOB)))
      # Number of jobs
      n_array_jobs = n_zsamples_splits * n_tnorm_models_ids
      cmd_scores_D = [
                    'lgbphs_scores_D.py',
                    '--group=%s' % group,
                    '--config-file=%s' % args.config_file,
                    '--grid'
                    ]
      job_scores_int = submit(jm, cmd_scores_D, dependencies=deps, array=(1,n_array_jobs,1), queue='q1d')
      job_scores_D.append(job_scores_int.id())
      print 'submitted:', job_scores_int

  # Merges the D matrices 
  job_scores_Dm = []
  cmd_scores_Dm =  [
                    'scores_D_merge.py',  
                    '--config-file=%s' % args.config_file, 
                    '--grid'
                  ]
  job_scores_Dm = submit(jm, cmd_scores_Dm, dependencies=job_scores_D) 
  print 'submitted:', job_scores_Dm
 
  # Computes the ZT-Norm
  job_scores_ZT = []
  if config.zt_norm:
    cmd_scores_ZT = [ 
              'scores_ztnorm.py', 
              '--config-file=%s' % args.config_file, 
              '--grid'
              ]

  job_scores_ZT = submit(jm, cmd_scores_ZT, dependencies=[job_scores_Am.id(), job_scores_Bm.id(),job_scores_Cm.id(), job_scores_Dm.id()], queue='q1d')
  print 'submitted:', job_scores_ZT 

  # Concatenates the scores
  cmd_cat = [ 
              'concatenate_scores.py', 
              '--config-file=%s' % args.config_file, 
              '--grid'
            ]
  job_cat = submit(jm, cmd_cat, dependencies=[job_scores_Am.id(), job_scores_ZT.id()], array=None)
  print 'submitted:', job_cat


if __name__ == '__main__':
  main()
