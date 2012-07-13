from setuptools import setup, find_packages

setup(
    name='antispoofing.verification.gmm',
    version='1.0',
    description='Replay-Attack Face Verification Package Based on a Parts-Based Gaussian Mixture Models',
    license='LICENSE.txt',

    author='Andre Anjos',
    author_email='andre.anjos@idiap.ch',

    packages=find_packages(),

    entry_points={
      'console_scripts': [
        'feature_extract.py = antispoofing.verification.gmm.script.feature_extract:main',
        'train_ubm.py = antispoofing.verification.gmm.script.train_ubm:main',
        'generate_statistics.py = antispoofing.verification.gmm.script.generate_statistics:main',
        'enrol.py = antispoofing.verification.gmm.script.enrol:main',
        'score.py = antispoofing.verification.gmm.script.score:main',

        #'plot_scores_and_counterm.py = antispoofing.verification.gmm.script.plot_scores_and_counterm:main',
        #'plot_scores.py = antispoofing.verification.gmm.script.plot_scores:main',
        'replay_perf_table.py = antispoofing.verification.gmm.script.replay_perf_table:main',
        #'show_culprit.py = antispoofing.verification.gmm.script.show_culprit:main',
        ],
      },

    long_description=open('doc/readme.rst').read(),

    install_requires=[
        "bob",      # base signal proc./machine learning library
        "argparse", # better option parsing
    ],
)
