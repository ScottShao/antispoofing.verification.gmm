#!/bin/bash

config_file="/idiap/user/lelshafey/work/experiments/faceverif_lib/config/pca_mobio_male.py"

./shell.py -- script/pca_tmodels.py -c $config_file -g dev
./shell.py -- script/pca_tmodels.py -c $config_file -g eval

./shell.py -- script/pca_models.py -c $config_file -g dev
./shell.py -- script/pca_models.py -c $config_file -g eval

./shell.py -- script/pca_scores_A.py -c $config_file -g dev
./shell.py -- script/pca_scores_A.py -c $config_file -g eval
./shell.py -- script/gmm_scores_A_merge.py -c $config_file

./shell.py -- script/pca_scores_B.py -c $config_file -g dev
./shell.py -- script/pca_scores_B.py -c $config_file -g eval
./shell.py -- script/gmm_scores_B_merge.py -c $config_file

./shell.py -- script/pca_scores_C.py -c $config_file -g dev
./shell.py -- script/pca_scores_C.py -c $config_file -g eval
./shell.py -- script/gmm_scores_C_merge.py -c $config_file

./shell.py -- script/pca_scores_D.py -c $config_file -g dev
./shell.py -- script/pca_scores_D.py -c $config_file -g eval
./shell.py -- script/gmm_scores_D_merge.py -c $config_file

./shell.py -- script/gmm_scores_ztnorm.py -c $config_file
./shell.py -- script/concatenate_scores.py -c $config_file

