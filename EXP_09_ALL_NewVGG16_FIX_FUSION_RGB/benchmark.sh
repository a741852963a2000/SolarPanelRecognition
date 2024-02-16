#!/bin/bash

for var in $(seq 1 10)
do
  rm weight/ALL_NewVGG16_FIX_FUSION.h5
  python3 Trainer.py
  sleep 30s
  python3 Evaluation.py >> benchmark0.txt
  sleep 30s
  python3 Finetune.py
  sleep 30s
  python3 Evaluation.py >> benchmark1.txt
  sleep 30s
  python3 Finetune2.py
  sleep 30s
  python3 Evaluation.py >> benchmark2.txt
  sleep 30s
done