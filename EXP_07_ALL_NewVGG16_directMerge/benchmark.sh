#!/bin/bash

for var in $(seq 1 10)
do
  rm weight/ALL_NewVGG16_directMerge.h5
  python3 Trainer.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  sleep 100s
done