#!/bin/bash

for var in $(seq 1 6)
do
  echo $var
  rm weight/FUSION_Baseline.h5
  python3 Trainer.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  echo $var
  sleep 100s
done