.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Mon 23 Jan 2012 11:37:14 CET

==================================================================
 TABULA RASA Baseline Verification for the Replay Attack Database
==================================================================

This document describes how to run the baseline face verification system chosen
by TABULA RASA on the Replay Attack database or any of its protocol variants.
It explains how to setup this package, generate UBM, client models and finally,
scores as well as how to generate the plots from those.

1. Setup
--------

Create the following links on the root of the directory of the package (where
this README file is). Make sure to select your *own* local versions of bob and
gridtk to avoid surprises like nightly build changes and the such.

.. code-block:: sh

  $ ln -s /idiap/home/aanjos/work/bob bob
  $ ln -s /idiap/home/aanjos/work/gridtk gridtk

2. Configuration
----------------

Tune configuration at: ``config/gmm_replay.py``:

.. code-block:: sh

  $ vim config/gmm_replay.py

Make sure, for instance, that the base output directory is set as you need. All
generated material will be output there. If you want to reproduce the TABULA
RASA baseline, don't change any of the parameters found in there, except for
input/output directories for the scripts.

3. Feature Extraction
---------------------

Run ``replay_dct_features.py`` to create the features. This step only need the
original database videos as input. It will generate, per video, all input
features required by the scripts that follow this one.

.. code-block:: sh

  $ ./shell.py -- script/replay_dct_features.py --config-file=config/gmm_replay.py

This will run through the 1300 videos in the database and extract the features
at the frame intervals defined at the configuration. You can execute everything
in parallel, at the SGE grid by doing like this:

.. code-block:: sh

  $ ./shell.py -- script/grid_replay_dct_features.py --config-file=config/gmm_replay.py

4. UBM Training
---------------

Run ``gmm_ubm_replay.py`` to create the UBM from selected features.

.. note::

  Note: if you use ~1k files, it will take ~3 hours to complete and there is no
  way to split it on the grid.  This step requires all features for the
  training set/enrollment are calculated.

.. code-block:: sh

  $ ./shell.py -- script/gmm_ubm_replay.py --config-file=config/gmm_replay.py

5. UBM Statistics Generation
----------------------------

Run ``gmm_stats_replay.py`` to create the background statistics for all
datafiles so we can run score normalization later. This step requires that the
UBM is calculated and all features are available.

.. code-block:: sh

  $ ./shell.py -- script/gmm_stats_replay.py --config-file=config/gmm_replay.py

This will take a lot of time to go through all the videos in the replay
database. You can optionally submit the command to the grid, if you are at
Idiap, with the following:

.. code-block:: sh

  $ ./shell.py -- ./script/grid_gmmstats_replay.py --config-file=config/gmm_replay.py

This command will spread the GMM UBM statistics calculation over 840 processes
that will run in about 5-10 minutes each. So, the whole job will take a few
hours to complete - taking into consideration current settings for SGE at
Idiap.

6. Client Model training
------------------------

Generate the models for all clients. Note: You can do this in parallel with
step 5 above as it only depends on the input features pre-calculated at step 3.

.. code-block:: sh

  $ ./shell.py -- ./script/gmm_models_replay.py --config-file=config/gmm_replay.py

If you think the above job is too slow, you also have a grid alternative:

.. code-block:: sh

  $ ./shell.py -- ./script/grid_gmmmodels_replay.py --config-file=config/gmm_replay.py

7. Scoring
----------

In this step you will score the videos (every N frames up to a certain frame
number) against the generated client models. We do this exhaustively for both
the test and development data. Command line execution goes like this:

.. code-block:: sh

  $ ./shell.py -- ./script/gmm_scores_replay.py --config-file=config/gmm_replay.py

Linear scoring is fast, but you can also submit a client-based break-down of
this problem like this:

.. code-block:: sh

  $ ./shell.py -- ./script/grid_gmmscores_replay.py --config-file=config/gmm_replay.py

8. Performance Figures
----------------------

After scores are calculated, you need to put them together to setup development
and test text files in either 4 or 5 column formats. To do that, use the
application ``replay_perf_table.py``:

.. code-block:: sh

  $ ./shell.py -- ./script/replay_perf_table.py --config-file=config/gmm_replay.py

9. Score Histograms
-------------------

You can plot the histograms of scores distributions using the following
command:

.. code-block:: sh

  $ ./shell.py -- script/plot_scores.py /idiap/temp/aanjos/spoofing/verif/performance/test-base-thourough-verif.4c /idiap/temp/aanjos/spoofing/verif/performance/test-photo-220.4c --overlay-protocol="Photo Attack" --title="Baseline GMM and PHOTO-ATTACK (spoofs) - Test set"

You can plot performance tables with the following command:

.. code-block:: sh

  $ ./shell.py -- compute_perf.py --no-plot --devel=/idiap/temp/aanjos/spoofing/verif/performance/devel-base-thourough-verif.4c --test=/idiap/temp/aanjos/spoofing/verif/performance/test-base-thourough-verif.4c
