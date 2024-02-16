#!/bin/bash

for var in $(seq 1 9)
do
  rm weight/InceptionV3_Transfer.h5
  python3 Trainer.py
  sleep 100s
  python3 Finetune.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  sleep 100s
done