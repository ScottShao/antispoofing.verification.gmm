from setuptools import setup, find_packages

setup(
    name='spoofverif',
    version='0.1',
    description='Replay-Attack Face Verification Package',

    #url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',

    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    packages=find_packages(),

    entry_points={
      'console_scripts': [
        'gmm_models_replay.py = spoofverif.script.gmm_models_replay:main',
        'gmm_scores_replay.py = spoofverif.script.gmm_scores_replay:main',
        'gmm_stats_replay.py = spoofverif.script.gmm_stats_replay:main',
        'gmm_ubm_replay.py = spoofverif.script.gmm_ubm_replay:main',
        'grid_gmmmodels_replay.py = spoofverif.script.grid_gmmmodels_replay:main',
        'grid_gmmscores_replay.py = spoofverif.script.grid_gmmscores_replay:main',
        'grid_gmmstats_replay.py = spoofverif.script.grid_gmmstats_replay:main',
        'grid_replay_dct_features.py = spoofverif.script.grid_replay_dct_features:main',
        'plot_scores_and_counterm.py = spoofverif.script.plot_scores_and_counterm:main',
        'plot_scores.py = spoofverif.script.plot_scores:main',
        'replay_dct_features.py = spoofverif.script.replay_dct_features:main',
        'replay_perf_table.py = spoofverif.script.replay_perf_table:main',
        'show_culprit.py = spoofverif.script.show_culprit:main',
        ],
      },

    long_description=open('doc/readme.rst').read(),

    install_requires=[
        "bob",      # base signal proc./machine learning library
        "argparse", # better option parsing
        "gridtk",   # SGE job submission at Idiap
    ],
)
