#!/bin/bash

for var in $(seq 1 1)
do
  echo $var
  rm weight/MS_NewVGG16.h5
  python3 Trainer.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  echo $var
  sleep 100s
done