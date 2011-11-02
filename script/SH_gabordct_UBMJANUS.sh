#!/bin/bash


for j in `seq 0 5`; do
  for i in `seq 0 6`; do
    ./shell.py -- script/gmm_ubm.py -c config/gabordct_banca_f${j}o${i}.py&
  done
  ./shell.py -- script/gmm_ubm.py -c config/gabordct_banca_f${j}o7.py  
done
