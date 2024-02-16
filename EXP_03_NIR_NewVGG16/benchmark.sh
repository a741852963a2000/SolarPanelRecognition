#!/bin/bash

for var in $(seq 1 10)
do
  rm weight/NIR_NewVGG16.h5
  python3 Trainer.py
  sleep 30s
  python3 Evaluation.py >> benchmark.txt
  sleep 30s
done