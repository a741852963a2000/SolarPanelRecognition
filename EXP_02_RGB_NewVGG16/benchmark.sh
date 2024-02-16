#!/bin/bash

for var in $(seq 1 1)
do
  rm weight/RGB_NewVGG16.h5
  python3 Trainer.py
  sleep 100s
  python3 Evaluation.py >> benchmark.txt
  sleep 100s
done