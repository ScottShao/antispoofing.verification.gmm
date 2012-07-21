=============================================================
 Parts-Based GMM Verification for the Replay Attack Database
=============================================================

This `Bob <http://www.idiap.ch/software/bob/>`_ satellite package allows you to
run a baseline Parts-Based GMM face verification system on the Replay Attack
Database. It explains how to setup this package, generate the Universal
Background Model (UBM), client models and finally, scores.

If you use this package and/or its results, please cite the following
publications.

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

If you wish to report problems or improvements concerning this code, please
contact `André Anjos <mailto:andre.anjos@idiap.ch>`_ and/or `Sébastien Marcel
<mailto:sebastien.marcel@idiap.ch>`_.

Installation
------------

This satellite package for `Bob <http://www.idiap.ch/software/bob/>`_ can be
installed with `Buildout <http://www.buildout.org/>`_. You don't have to have
``Buildout`` installed or even know what it is to make use of this package.
Just follow the instructions bellow.

The first thing to do is to `install Bob
<https://github.com/idiap/bob/wiki/Releases>`_ if you haven't done so already.

The second thing to do is to `install the Replay Attack database
<http://www.idiap.ch/dataset/replayattack/>`_ as explained in that web site.
Save the base directory name in which you unpacked the database files and use
it for the Feature Extraction phase bellow.

.. warning::

  This satellite package has been validated to work against ``Bob-1.0.5``. More
  recent versions of the ``1.0.x`` branch may work, but no test has been done.
  If you find difficulties reproducing the results in this package, make sure
  you are using that precise version of ``Bob``.

If you have `Bob` installed centrally
=====================================

If you have ``Bob`` installed by your system administrator, centrally, you just
do::

  $ python bootstrap.py
  $ bin/buildout

And you are ready to start using the package.

If you have compiled `Bob` yourself
===================================

If you installed ``Bob`` in a location in which Python does not look by default,
you will have to do a little editing on ``localbob.cfg`` to define the root
directory containing the version of ``Bob`` you want to use and, then::

  $ python bootstrap.py
  $ bin/buildout -c localbob.cfg

.. note::

  You should use always the same Python interpreter you used to compile ``Bob``
  with.

Configuration Tweaking (optional)
---------------------------------

The current scripts have been tunned to reproduce the results presented on some
of our publications (as indicated above), as well as on FP7 Project `TABULA
RASA <http://www.tabularasa-euproject.org/>`_ reports.  They still accept an
alternate (python) configuration file that can be passed as input. If nothing
is passed, a default configuration file located at
``antispoofing/verification/gmm/config/gmm_replay.py`` is used. Copy that file
to the current directory and edit it to modify the overall configuration for
the mixture-model system or for the (DCT-based) feature extraction. Use the
option ``--config=myconfig.py`` to set your private configuration if you decide
to do so. Remember to set the option thoroughly through out all script calls or
unexpected results may happen.

Running the Experiments
-----------------------

Follow the sequence described here to reproduce paper results.

Run ``feature_extract.py`` to extract the DCT block features. This step is
the only that requires the original database videos as input. It will generate,
**per video frame**, all input features required by the scripts that follow
this one::

  $ ./bin/feature_extract.py /root/of/replay/attack/database results/dct

This will run through the 1300 videos in the database and extract the features
at the frame intervals defined at the configuration. In a relatively fast
machine, it will take about 10-20 seconds per input video, with a frame-skip
parameter set to 10 (the default). If you want to be thorough, you will need to
parallelize this script so that the overall database can be processed in a
reasonable amount of time.

You can parallelize the execution of the above script (and of some of the
scripts below as well) if you are a Idiap. Just do the following instead::

  $ ./bin/jman submit --array=1300 ./bin/feature_extract.py /root/of/replay/attack/database results/dct --grid

Notice the ``--array=1300`` and ``--grid`` option by the end of the script. The
above instruction tells SGE to run 1300 versions of my script with the same
input parameters. The only difference is ``SGE_TASK_ID`` environment variable
that is changed at every interation (thanks to the ``--array=1300`` option).
The ``--grid`` option the execution of the script analyze first the value of
``SGE_TASK_ID`` and re-set the internal processing so that particular instance
of ``feature_extract.py`` only processes one of the 1300 videos that requires
processing. You can check the status of the jobs in the grid with ``jman
refresh`` (refer to the `GridTk manual <http://packages.python.org/gridtk>` for
details).

.. note::

  If you are not, you can still take a look at our `GridTk package
  <http://pypi.python.org/pypi/gridtk>`_ for a logging grid job manager for SGE.

UBM Training
------------

Run ``train_ubm.py`` to create the GMM Universal Background Model from selected
features (in the enrollment/training subset).

.. note::

  Note: if you use ~1k files, it will take a few hours to complete and there is
  currently no way to parallelize this.  This step requires all features for
  the training set/enrollment are calculated. The job can take many gigabytes
  of physical memory from your machine, so we advise you to run it in a machine
  with, at least, 8 gigabytes of free memory.

.. code-block:: sh

  $ ./bin/train_ubm.py results/dct results/ubm.hdf5

Unfortunately, you cannot easily parallelize this job. Nevertheless, you can
submit it to the grid with the following command and avoid it to run on your
machine (nice if you have a busy day of work)::

  $ ./bin/jman submit --queue=q_1week --memory=8G ./bin/train_ubm.py results/dct results/ubm.hdf5

Even if you choose a long enough queue, it is still prudent to set the memory
requirements for the node you will be assigned to, to guarantee a minimum
amount of memory.

UBM Statistics Generation
-------------------------

Run ``generate_statistics.py`` to create the background statistics for all
datafiles so we can calculate scores later. This step requires that the UBM is
trained and all features are available::

  $ ./bin/generate_statistics.py results/dct results/ubm.hdf5 results/stats

This will take a lot of time to go through all the videos in the replay
database. You can optionally submit the command to the grid, if you are at
Idiap, with the following::

  $ ./bin/jman submit --array=840 ./bin/generate_statistics.py results/dct results/ubm.hdf5 results/stats --grid

This command will spread the GMM UBM statistics calculation over 840 processes
that will run in about 5-10 minutes each. So, the whole job will take a few
hours to complete - taking into consideration current settings for SGE at
Idiap.

Client Model training
---------------------

.. note::

  You can do this in parallel with the step above as it only depends on the
  input features pre-calculated at step 3

Generate the models for all clients::

  $ ./bin/enrol.py results/dct results/ubm.hdf5 results/models

If you think the above job is too slow, you can throw it at the grid as well::

  $ ./bin/jman submit --array=35 ./bin/enrol.py results/dct results/ubm.hdf5 results/models --grid

Scoring
-------

In this step you will score the videos (every N frames up to a certain frame
number) against the generated client models. We do this exhaustively for both
the test and development data. Command line execution goes like this::

  $ ./bin/score.py results/stats results/ubm.hdf5 results/models results/scores

Linear scoring is fast, but you can also submit a client-based break-down of
this problem like this::

  $ ./bin/jman submit --array=35 ./bin/score.py results/stats results/ubm.hdf5 results/models results/scores --grid

Full Score Files
----------------

After scores are calculated, you need to put them together to setup development
and test text files in a 4 or 5 column format. To do that, use the application
``build_score_files.py``. The next command will generate the baseline
verification results by thouroughly matching every client video against every
model available in the individual sets, averaging over (the first) 220 frames::

  $ ./bin/build_score_files.py results/scores results/perf --thorough --frames=220

You can specify to use the attack protocols like this (avoid using the
`--thourough` option)::

  $ ./bin/build_score_files.py results/scores results/perf --protocol=grandtest --frames=220

.. warning::

  It is possible you see warnings being emitted by the above programs in
  certain cases. This is **normal**. The warnings correspond to cases in which
  the program is trying to collect data from a certain frame number in which a
  face was not detected on the originating video.

Reproduce Paper Results
-----------------------

To reproduce our paper results (~82% of attacks passing the verification
system), you must generate two score files as defined above and then call a few
programs that compute the threshold on the development set and apply it to the
licit and spoofing test sets::

  $ ./bin/eval_threshold.py --scores=results/perf/devel-baseline-thourough-220.4c
  Threshold: 0.686207566
  FAR : 0.000% (0/840)
  FRR : 0.000% (0/60)
  HTER: 0.000%

  $ ./bin/apply_threshold.py --scores=results/perf/test-grandtest-220.4c --threshold=0.686207566
  FAR : 82.500% (330/400)
  FRR : 0.000% (0/80)
  HTER: 41.250%
