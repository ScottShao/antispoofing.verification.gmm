from setuptools import setup, find_packages

setup(
    name='antispoofing.verification.gmm',
    version='0.1',
    description='Replay-Attack Face Verification Package Based on Gaussian Mixture Models',
    license='LICENSE.txt',

    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    packages=find_packages(),

    entry_points={
      'console_scripts': [
        'gmm_models_replay.py = antispoofing.verification.gmm.script.gmm_models_replay:main',
        'gmm_scores_replay.py = antispoofing.verification.gmm.script.gmm_scores_replay:main',
        'gmm_stats_replay.py = antispoofing.verification.gmm.script.gmm_stats_replay:main',
        'gmm_ubm_replay.py = antispoofing.verification.gmm.script.gmm_ubm_replay:main',
        #'grid_gmmmodels_replay.py = antispoofing.verification.gmm.script.grid_gmmmodels_replay:main',
        #'grid_gmmscores_replay.py = antispoofing.verification.gmm.script.grid_gmmscores_replay:main',
        #'grid_gmmstats_replay.py = antispoofing.verification.gmm.script.grid_gmmstats_replay:main',
        #'grid_replay_dct_features.py = antispoofing.verification.gmm.script.grid_replay_dct_features:main',
        #'plot_scores_and_counterm.py = antispoofing.verification.gmm.script.plot_scores_and_counterm:main',
        #'plot_scores.py = antispoofing.verification.gmm.script.plot_scores:main',
        'replay_dct_features.py = antispoofing.verification.gmm.script.replay_dct_features:main',
        'replay_perf_table.py = antispoofing.verification.gmm.script.replay_perf_table:main',
        #'show_culprit.py = antispoofing.verification.gmm.script.show_culprit:main',
        ],
      },

    long_description=open('doc/readme.rst').read(),

    install_requires=[
        "bob",      # base signal proc./machine learning library
        "argparse", # better option parsing
        "gridtk",   # SGE job submission at Idiap
    ],
)
