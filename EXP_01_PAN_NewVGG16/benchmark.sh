#!/bin/bash

for var in $(seq 1 6)
do
  rm weight/PAN_NewVGG16.h5
  python3 Trainer.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  sleep 100s
done