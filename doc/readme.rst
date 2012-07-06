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

If you use this package, please refer to the following publications.

1. The Replay-Attack Database and baseline GMM results for it::

    @inproceedings{Chingovska_BIOSIG_2012,
      author = {I. Chingovska AND A. Anjos AND S. Marcel},
      keywords = {Attack, Counter-Measures, Counter-Spoofing, Face Recognition, Liveness Detection, Replay, Spoofing},
      month = sep,
      title = {On the Effectiveness of Local Binary Patterns in Face Anti-spoofing},
      booktitle = {IEEE BioSIG 2012},
      year = {2012},
  }

2. Bob as the core framework used for these results::

    @inproceedings{Anjos_ACMMM_2012,
        author = {A. Anjos AND L. El Shafey AND R. Wallace AND M. G\"unther AND C. McCool AND S. Marcel},
        title = {Bob: a free signal processing and machine learning toolbox for researchers},
        year = {2012},
        month = oct,
        booktitle = {20th ACM Conference on Multimedia Systems (ACMMM), Nara, Japan},
        publisher = {ACM Press},
    }

1. Setup
--------

This satellite package for `Bob <http://idiap.github.com/bob/>`_ can be
installed with `Buildout <http://www.buildout.org/>`_. You don't have to have
`Buildout` installed or even know what it is to make use of this package. Just
follow the instructions bellow.

The first thing to do is to `install Bob
<https://github.com/idiap/bob/wiki/Releases>`_ if you haven't done so already.

The second thing to do is to `install the Replay Attack database
<http://www.idiap.ch/dataset/replayattack/>`_ as explained in that web site.
Save the base directory name in which you unpacked the database files and use
it for the Feature Extraction phase bellow.

1.1 If you have `Bob` installed centrally
-----------------------------------------

If you have `Bob` installed by your system administrator, centrally, you just
do::

  $ python bootstrap.py
  $ bin/buildout

And you are ready to start using the package.

1.2 If you have compiled `Bob` yourself
---------------------------------------

If you installed `Bob` in a location in which Python does not look by default,
you will have to do a little editing on `localbob.cfg` to define the root
directory containing the version of `Bob` you want to use and, then::

  $ python bootstrap.py
  $ bin/buildout -c localbob.cfg

.. note::

  You should use always the same Python interpreter you used to compile `Bob`
  with.

2. Configuration
----------------

The current scripts have been tunned to reproduce the results presented on some
of our publications, as well as on TABULA RASA reports. Most of them still
accept a (python) configuration file that can be passed as input. If nothing is
passed, a default configuration file located at
`antispoofing/verification/gmm/config/gmm_replay.py` is used. Copy that file to
the current directory and edit it to modify the overall configuration for the
mixture-model system or for the (DCT-based) feature extraction.

If you modify the configuration file, make sure, for instance, that the base
output directory is set as per your requirements. All generated material will
be output there.

3. Running the Experiments
--------------------------

Follow the sequence described here to reproduce paper results.

Run ``replay_dct_features.py`` to create the features. This step is only need
the original database videos as input. It will generate, per video, all input
features required by the scripts that follow this one::

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
application ``replay_perf_table.py``. The next command will generate the
baseline verification results by thouroughly matching every client video
against every model available in the individual sets, averaging over 220
frames:

.. code-block:: sh

  $ ./shell.py -- ./script/replay_perf_table.py --thourough --frames=220 --config-file=config/gmm_replay.py

You can specify to use the attack protocols like this (avoid using the
`--thourough` option):

.. code-block:: sh

  $ ./shell.py -- ./script/replay_perf_table.py --protocol=grandtest --frames=220 --config-file=config/gmm_replay.py

There is a script called `script/create_all_tables.sh` that will run on all
common combinations of protocols and number of frames and will dump the output
on the `config.base_output_dir/performance/` directory. You can just call it:

.. code-block:: sh

  $ ./shell.py -- ./script/create_all_tables.sh

.. warning::

  It is possible you see warnings being emitted by the above programs in
  certain cases. This is **normal**. The warnings correspond to cases in which
  the program is trying to collect data from a certain frame number in which a
  face was not detected on the originating video.

9. Score Histograms and Performance Figures
-------------------------------------------

You can plot performance tables with the following command:

.. code-block:: sh

  $ ./shell.py -- compute_perf.py --no-plot --devel=/idiap/temp/aanjos/spoofing/verif/performance/devel-baseline-thourough-220.4c --test=/idiap/temp/aanjos/spoofing/verif/performance/test-baseline-thourough-220.4c


You can plot the histograms of scores distributions using the following
command:

.. code-block:: sh

  $ ./shell.py -- script/plot_scores.py /idiap/temp/aanjos/spoofing/verif/performance/test-baseline-thourough-220.4c /idiap/temp/aanjos/spoofing/verif/performance/test-photo-220.4c --overlay-protocol="Photo Attack" --title="Baseline GMM and PHOTO-ATTACK (spoofs) - Test set"

